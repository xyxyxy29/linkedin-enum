import requests
import re
import sys
from urllib.parse import quote
import time
import os
import csv
import argparse

def extract_organisation_id(url):
    try:
        headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }
        
        org_id_list = []
        org_url_list = url.split(',')
        
        for i in org_url_list:
            response = requests.get(i, headers=headers)

            if response.status_code == 200:
                organisation_id_list = re.findall(r'urn:li:organization:(.*?)"', response.text)
                
                if organisation_id_list:
                    org_id_list.append(organisation_id_list[0])
                else:
                    print(f"LinkedIn organisation ID from {i} not found.")
                    sys.exit(1)

            elif response.status_code == 403:
                print(f"HTTP 403 received. Cookie is invalid or your account has been restricted.")
                sys.exit(1)
            else:
                print(f"Failed to retrieve organisation ID from {i}. Status code: {response.status_code}")
                sys.exit(1)
                
        return org_id_list

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

def read_search_keys(search_key):
    try:
        if search_key.endswith('.txt'):
            with open(search_key, 'r') as file:
                return [line.strip() for line in file.readlines()]
        else:
            return [search_key.strip()]
    except Exception as e:
        print(f"An error occurred while reading search keys: {str(e)}")
        sys.exit(1)

def linkedin_search(search_key, cookie_li_at, organisation_id_list, country_id_list):
    try:
        search_key_encoded = quote(search_key, safe='')
        org_id_concat = ','.join(organisation_id_list)
        country_id_concat = ','.join(country_id_list)

        url = f"https://www.linkedin.com/voyager/api/graphql?variables=(start:0,origin:GLOBAL_SEARCH_HEADER,query:(keywords:{search_key_encoded},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:currentCompany,value:List({org_id_concat})),(key:geoUrn,value:List({country_id_concat})),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.838ad2ecdec3b0347f493f93602336e9"

        headers = {
            'Cookie': f"JSESSIONID=\"foo\"; li_at={cookie_li_at}",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Csrf-Token': 'foo',
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.text
        elif response.status_code == 403:
            print(f"HTTP 403 received. Cookie is invalid or your account has been restricted.")
            sys.exit(1)
        else:
            print(f"Failed to retrieve LinkedIn profile. Status code: {response.status_code}")
            return None
            
        

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def linkedin_search_list(search_keys, cookie_li_at, organisation_id, outfile_path, country_id_list):
    processed_count = 0
    remaining_keys = []

    for key in search_keys:
        if not key.strip() == '':
            response = linkedin_search(key, cookie_li_at, organisation_id, country_id_list)
            time.sleep(5)
            
            if response:
                linkedin_name_list = re.findall(r'FIRST_STRONG","_type":"com.linkedin.voyager.dash.common.text.TextViewModel","text":"(.*?)"', response)
                job_title_list = re.findall(r'primarySubtitle":{"textDirection":"USER_LOCALE","_type":"com.linkedin.voyager.dash.common.text.TextViewModel","text":"(.*?)"', response)
                profile_url_list = re.findall(r'com.linkedin.55ee9afd4182671fe7e271f615659525","url":"https://www.linkedin.com/in/(.*?)\?', response)

                if profile_url_list:
                    linkedin_name = linkedin_name_list[0]
                    job_title = job_title_list[0]
                    profile_url = profile_url_list[0]
                    
                    namecheck = linkedin_name + profile_url
                    
                    if job_title and all(word.lower() in namecheck.lower() for word in key.split()):
                        print(key + " | " + linkedin_name + " (Exact match) | " + job_title + " | https://www.linkedin.com/in/" + profile_url)
                        content = [key, linkedin_name, job_title, f"https://www.linkedin.com/in/{profile_url}", "Exact Match"]
                        write_file(outfile_path, content)
                    elif job_title and not all(word.lower() in namecheck.lower() for word in key.split()):
                        print(key + " | " + linkedin_name + " (Possible match) | " + job_title + " | https://www.linkedin.com/in/" + profile_url)
                        content = [key, linkedin_name, job_title, f"https://www.linkedin.com/in/{profile_url}", "Possible Match"]
                        write_file(outfile_path, content)
                    else:
                        print(key + ": Unable to retrieve job title. Profile URL: https://www.linkedin.com/in/" + profile_url)
                        content = [key, linkedin_name, "Not Found", f"https://www.linkedin.com/in/{profile_url}", "Potential Match"]
                        write_file(outfile_path, content)
                else:
                    print(key + ": User not found")
                    content = [key, "Not Found", "Not Found", "Not Found"]
                    write_file(outfile_path, content)

            else:
                remaining_keys.append(key)

            processed_count += 1

            # Pause after 50 users
            if processed_count % 50 == 0:
                print("Pausing for 1 minute...")
                time.sleep(60)

    if remaining_keys:
        remaining_file_path = outfile_path.replace('.csv', '_remaining.txt')
        with open(remaining_file_path, 'w') as file:
            for key in remaining_keys:
                file.write(key + '\n')
        print(f"Remaining search keys saved to {remaining_file_path}")

def check_existing_outfile(outfile_path):
    if os.path.exists(outfile_path):
        user_input = input(f"The file '{outfile_path}' already exists. Do you want to overwrite it? (y/n): ").lower()
        if user_input == 'y':
            with open(outfile_path, 'w', newline='', encoding='utf-8') as csvfile:
                data = ["Key", "Full Name", "Job Title", "LinkedIn URL", "Match Type"]
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(data)
                return
        elif user_input == 'n':
            print("File not overwritten. Exiting.")
            sys.exit(1)
        else:
            print("Command not recognised. Exiting.")
            sys.exit(1)
    else:
        with open(outfile_path, 'w', newline='', encoding='utf-8') as csvfile:
            data = ["Key", "Full Name", "Job Title", "LinkedIn URL", "Match Type"]
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(data)
            return

def write_file(outfile_path, content):
    with open(outfile_path, 'a', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(content)

def get_filter_country(country_list, cookie_li_at):
    try:
        country_list_encoded = quote(country_list, safe='')
        url = f"https://www.linkedin.com/voyager/api/graphql?variables=(keywords:{country_list_encoded},query:(typeaheadFilterQuery:(geoSearchTypes:List(MARKET_AREA,COUNTRY_REGION,ADMIN_DIVISION_1,CITY))),type:GEO)&queryId=voyagerSearchDashReusableTypeahead.23c9f700d1a32edbb7f6646dda5e7480"

        headers = {
            'Cookie': f"JSESSIONID=\"foo\"; li_at={cookie_li_at}",
            'Csrf-Token': 'foo',
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.text

            countries = re.findall(r'"text":"(.*?)"', data)
            country_ids = re.findall(r'"trackingUrn":"urn:li:geo:(.*?)"', data)

            print("Select countries:")
            for i, country in enumerate(countries, start=1):
                print(f"{i}. {country}")

            selected_indices = input("Enter the indices of the countries you want to select (comma-separated): ")
            selected_indices = [int(index) - 1 for index in selected_indices.split(',')]

            valid_indices = [index for index in selected_indices if 0 <= index < len(countries)]
            selected_countries = [countries[index] for index in valid_indices]
            selected_country_ids = [country_ids[index] for index in valid_indices]

            return selected_country_ids

        else:
            print(f"Failed to retrieve country IDs. Status code: {response.status_code}")
            return []

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Scraper")
    parser.add_argument("--companyurl", help="LinkedIn company URL. Separate multiple URLs with a comma.", required=True)
    parser.add_argument("--search", help="Search key or path to a file containing search keys", required=True)
    parser.add_argument("--cookie", help="li_at cookie value", required=True)
    parser.add_argument("--outfile", help="Output CSV file path", required=True)
    parser.add_argument("--country", help="Country to filter", required=True)
    
    args = parser.parse_args()
    
    url = args.companyurl
    search_key_input = args.search
    cookie_li_at = args.cookie
    outfile_path = args.outfile
    country_list = args.country

    # Check if outfile exists
    check_existing_outfile(outfile_path)

    # Retrieve LinkedIn organisation id
    organisation_id = extract_organisation_id(url)

    # Read search keys from file or use the provided string
    search_keys = read_search_keys(search_key_input)
    
    # Get filter country IDs
    country_id_list = get_filter_country(country_list, cookie_li_at)

    try:
        # Call the linkedin_search function for each search key and get the results
        linkedin_search_list(search_keys, cookie_li_at, organisation_id, outfile_path, country_id_list)
    
    except Exception as e:
        print(f"An error occurred during processing: {str(e)}")
        remaining_keys = [key for key in search_keys if not any(key in line for line in open(outfile_path))]
        if remaining_keys:
            remaining_file_path = outfile_path.replace('.csv', '_remaining.txt')
            with open(remaining_file_path, 'w') as file:
                for key in remaining_keys:
                    file.write(key + '\n')
            print(f"Remaining search keys saved to {remaining_file_path}")

if __name__ == "__main__":
    main()
