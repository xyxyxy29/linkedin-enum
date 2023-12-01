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
            else:
                return f"Failed to retrieve organisation ID from {i}. Status code: {response.status_code}"
                sys.exit(1)
                
        return org_id_list

    except Exception as e:
            return f"An error occurred: {str(e)}"
            sys.exit(1)

def read_search_keys(search_key):
    try:
        # If search_key is a file, read the file and return a list of search keys
        if search_key.endswith('.txt'):
            with open(search_key, 'r') as file:
                return [line.strip() for line in file.readlines()]
        else:
            # If search_key is a string, return a list with the single string
            return [search_key.strip()]
    except Exception as e:
        return f"An error occurred while reading search keys: {str(e)}"
        sys.exit(1)

def linkedin_search(search_key, cookie_li_at, organisation_id_list, country_id_list):
    try:
        search_key_encoded = quote(search_key, safe='')
        
        org_id_concat = ','.join(organisation_id_list)
        
        country_id_concat = ','.join(country_id_list)
        
        url = f"https://www.linkedin.com/voyager/api/graphql?variables=(start:0,origin:GLOBAL_SEARCH_HEADER,query:(keywords:{search_key_encoded},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:currentCompany,value:List({org_id_concat})),(key:geoUrn,value:List({country_id_concat})),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.994bf4e7d2173b92ccdb5935710c3c5d"

        headers = {
            'Cookie': f"JSESSIONID=\"foo\"; li_at={cookie_li_at}",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Csrf-Token': 'foo',
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.text
            profile_url_values = re.findall(r'"navigationUrl":"https://www.linkedin.com/in/(.*?)\?', data) 
            
            if profile_url_values:
                profile_url = profile_url_values[0]
                return profile_url

        else:
            return f"Failed to retrieve LinkedIn profile. Status code: {response.status_code}"

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
    
def get_profile_id(profile_url_path, cookie_li_at):
    try:
        url = f"https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(vanityName:{profile_url_path})&queryId=voyagerIdentityDashProfiles.0bc93b66ba223b9d30d1cb5c05ff031a"

        headers = {
            'Cookie': f"JSESSIONID=\"foo\"; li_at={cookie_li_at}",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Csrf-Token': 'foo',
        }            

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.text
            profile_id = re.findall(r'"urn:li:fsd_profilePosition:\((.*?),', data)
            
            if profile_id:
                return profile_id[0]

        else:
            return f"Failed to retrieve profile ID. Status code: {response.status_code}"     

    except Exception as e:
        return f"An error occurred: {str(e)}"
        
        
def get_job_title(profile_id, cookie_li_at):
    try:
        url = f"https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{profile_id})&queryId=voyagerIdentityDashProfileCards.004536ac07d237fe4177532af520f57d"

        headers = {
            'Cookie': f"JSESSIONID=\"foo\"; li_at={cookie_li_at}",
            'Csrf-Token': 'foo', 
        }            

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.text
            extract = re.findall(r'experience_company_logo(.*?)406952', data)
            
            if not extract:
                extract = re.findall(r'experience_company_logo(.*?)15235388', data)
                job_title = re.findall(r'"text":"(.*?)"', extract[0])
            
            else:
                
                job_title = re.findall(r'"text":"(.*?)"', extract[0])
            
            if job_title:
                return job_title[-1]

                
        else:
            return f"Failed to retrieve job title. Status code: {response.status_code}"     

    except Exception as e:
        return f"An error occurred: {str(e)}"
        
        
def get_name(profile_id, cookie_li_at):
    try:
        url = f"https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{profile_id})&queryId=voyagerIdentityDashProfileCards.fcc08769f74e2381321c2f1f2371561c"

        headers = {
            'Cookie': f"JSESSIONID=\"foo\"; li_at={cookie_li_at}",
            'Csrf-Token': 'foo', 
        }            

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.text
            firstname = re.findall(r'"firstName":"(.*?)"', data)
            
            lastname = re.findall(r'"lastName":"(.*?)"', data)
            fullname= firstname[0] + " " + lastname[0]
            
            if fullname:
                return fullname
                


                
        else:
            return f"Failed to retrieve LinkedIn name. Status code: {response.status_code}"     

    except Exception as e:
        return f"An error occurred: {str(e)}"
        
        
def linkedin_search_list(search_keys, cookie_li_at, organisation_id, outfile_path, country_id_list):
    for key in search_keys:
        if not key.strip()== '':
            # get linkedin profile url
            profile_url = linkedin_search(key, cookie_li_at, organisation_id, country_id_list)
            
            if profile_url:
            
                # get profile id
                profile_id = get_profile_id(profile_url, cookie_li_at)
                
                if profile_id:
                    
                    # get name
                    fullname = get_name(profile_id, cookie_li_at)
                    
                    
                    # get job title
                    job_title = get_job_title(profile_id, cookie_li_at)
                    
                    namecheck = fullname + profile_url
                   
                    
                    if job_title and all(word.lower() in namecheck.lower() for word in key.split()):
                        print(key + " | " + fullname + " (Exact match) | " + job_title + " | https://www.linkedin.com/in/" + profile_url)
                        
                        content = [key, fullname, job_title, f"https://www.linkedin.com/in/{profile_url}", "Exact Match"]
                        write_file(outfile_path,content)
                        
                    elif job_title and not all(word.lower() in namecheck.lower() for word in key.split()):
                        print(key + " | " + fullname + " (Possible match) | " + job_title + " | https://www.linkedin.com/in/" + profile_url)
                        content = [key, fullname, job_title, f"https://www.linkedin.com/in/{profile_url}", "Possible Match"]
                        write_file(outfile_path,content)


                    else:
                        print(key + ": Unable to retrieve job title. Profile URL: https://www.linkedin.com/in/" + profile_url)
                        content = [key, fullname, "Not Found", f"https://www.linkedin.com/in/{profile_url}", "Potential Match"]
                        write_file(outfile_path,content)

                        
                        
                    
                else:
                    print(key + ": Unable to extract profile ID.")
                    content = [key, fullname, "Not Found", f"https://www.linkedin.com/in/{profile_url}", "Potential Match"]
                    write_file(outfile_path,content)
            else:
                print(key + ": User not found in specified organisation.")
                content = [key, "Not Found", "Not Found", "Not Found"]
                write_file(outfile_path,content) 
                
        else:
                print(key + ": Invalid search key provided.")
                content = [key, "Invalid Search Key"]
                write_file(outfile_path,content) 
        time.sleep(1) 
        

def check_existing_outfile(outfile_path):
   # Check if the file already exists
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

            # Prompt user to select a subset of countries
            print("Select countries:")
            for i, country in enumerate(countries, start=1):
                print(f"{i}. {country}")

            selected_indices = input("Enter the indices of the countries you want to select (comma-separated): ")
            selected_indices = [int(index) - 1 for index in selected_indices.split(',')]

            # Validate selected indices
            valid_indices = [index for index in selected_indices if 0 <= index < len(countries)]
            selected_countries = [countries[index] for index in valid_indices]
            selected_country_ids = [country_ids[index] for index in valid_indices]

            return selected_country_ids

        else:
            return f"Failed to retrieve country IDs. Status code: {response.status_code}"

    except Exception as e:
        return f"An error occurred: {str(e)}"
        



def main():
    parser = argparse.ArgumentParser(description="LinkedIn Scraper")
    parser.add_argument("--companyurl", help="LinkedIn company URL. Separate multiple URLs with a comma.")
    parser.add_argument("--search", help="Search key or path to a file containing search keys")
    parser.add_argument("--cookie", help="li_at cookie value")
    parser.add_argument("--outfile", help="Output CSV file path")
    parser.add_argument("--country", help="Country to filter")
    
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
    
    country_id_list = get_filter_country(country_list,cookie_li_at)

    # Call the linkedin_search function for each search key and get the results
    linkedin_search_list(search_keys, cookie_li_at, organisation_id, outfile_path, country_id_list)

if __name__ == "__main__":
    main()

        
