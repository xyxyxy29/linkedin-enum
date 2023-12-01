import requests
import re
import sys
from urllib.parse import quote
import time
import os

def extract_organisation_id(url):
    try:
        headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            organisation_id_list = re.findall(r'urn:li:organization:(.*?)"', response.text)
            if organisation_id_list:
                return organisation_id_list[0]
            else:
                print("LinkedIn organisation ID not found.")
                sys.exit(1)
        else:
            return f"Failed to retrieve organisation ID. Status code: {response.status_code}"
            sys.exit(1)

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

def linkedin_search(search_key, cookie_li_at, organisation_id):
    try:
        search_key_encoded = quote(search_key, safe='')
        url = f"https://www.linkedin.com/voyager/api/graphql?variables=(start:0,origin:GLOBAL_SEARCH_HEADER,query:(keywords:{search_key_encoded},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:currentCompany,value:List({organisation_id})),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&queryId=voyagerSearchDashClusters.a2c8fa93b136d262362dfeaa5b857b62"

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
        
        
def get_job_title(profile_id, cookie_li_at, organisation_id):
    try:
        url = f"https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(profileUrn:urn%3Ali%3Afsd_profile%3A{profile_id})&queryId=voyagerIdentityDashProfileCards.004536ac07d237fe4177532af520f57d"

        headers = {
            'Cookie': f"JSESSIONID=\"foo\"; li_at={cookie_li_at}",
            'Csrf-Token': 'foo', 
        }            

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.text
            extract = re.findall(rf'experience_company_logo(.*?){organisation_id}', data)
            job_title = re.findall(r'"text":"(.*?)"', extract[0])
            
            if job_title:
                return job_title[-1]

                
        else:
            return f"Failed to retrieve job title. Status code: {response.status_code}"     

    except Exception as e:
        return f"An error occurred: {str(e)}"
        
        
def get_name(profile_id, cookie_li_at, organisation_id):
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
        
        
def linkedin_search_list(search_keys, cookie_li_at, organisation_id, outfile):
    for key in search_keys:
        if not key.strip()== '':
            # get linkedin profile url
            profile_url = linkedin_search(key, cookie_li_at, organisation_id)
            
            if profile_url:
            
                # get profile id
                profile_id = get_profile_id(profile_url, cookie_li_at)
                
                if profile_id:
                    
                    # get name
                    fullname = get_name(profile_id, cookie_li_at, organisation_id)
                    
                    
                    # get job title
                    job_title = get_job_title(profile_id, cookie_li_at, organisation_id)
                    
                    namecheck = fullname + profile_url
                   
                    
                    if job_title and all(word.lower() in namecheck.lower() for word in key.split()):
                        print(key + " | " + fullname + " (Exact match) | " + job_title + " | https://www.linkedin.com/in/" + profile_url)
                        content = key + ',"' + job_title + '",https://www.linkedin.com/in/' + profile_url + ",Exact Match"
                        write_file(outfile_path,content)
                        
                    elif job_title and not all(word.lower() in namecheck.lower() for word in key.split()):
                        print(key + " | " + fullname + " (Possible match) | " + job_title + " | https://www.linkedin.com/in/" + profile_url)
                        content = key + ',"' + job_title + '",https://www.linkedin.com/in/' + profile_url + ",Potential Match"
                        write_file(outfile_path,content)


                    else:
                        print(key + ": Unable to retrieve job title. Profile URL: https://www.linkedin.com/in/" + profile_url)
                        content = key + "," + "Not Found" + ",https://www.linkedin.com/in/" + profile_url + ",Potential Match"
                        write_file(outfile_path,content)

                        
                        
                    
                else:
                    print(key + ": Unable to extract profile ID.")
                    content = key + "," + "Not Found" + ",https://www.linkedin.com/in/" + profile_url + ",Potential Match"
                    write_file(outfile_path,content)
            else:
                print(key + ": User not found in specified organisation.")
                content = key + "," + "Not Found" + "," + "Not Found"
                write_file(outfile_path,content) 
                
        else:
                print(key + ": Invalid search key provided.")
                content = key + "," + "Not Found" + "," + "Not Found"
                write_file(outfile_path,content) 
        time.sleep(1) 
        

def check_existing_outfile(outfile_path):
   # Check if the file already exists
    if os.path.exists(outfile_path):
        user_input = input(f"The file '{outfile_path}' already exists. Do you want to overwrite it? (y/n): ").lower()

        if user_input == 'y':
            with open(outfile_path, 'w') as file:
                file.write("Name,Job Title,LinkedIn URL,Match\n")
                return

        elif user_input == 'n':
            print("File not overwritten. Exiting.")
            sys.exit(1)
            
        else:
            print("Command not recognised. Exiting.")
            sys.exit(1)
    
    else:
        with open(outfile_path, 'w') as file:
            file.write("Name,Job Title,LinkedIn URL,Match\n")
            return
        
    
def write_file(outfile_path, content):
    with open(outfile_path, 'a', encoding='utf-8') as file:
        file.write(content)
        file.write("\n")
        



if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <linkedin_company_url> <search_key_or_file> <li_at_cookie_value> <csv_outfile>")
        sys.exit(1)

    url = sys.argv[1]
    search_key_input = sys.argv[2]
    cookie_li_at = sys.argv[3]
    outfile_path = sys.argv[4]
    
    # Check if outfile exists
    check_existing_outfile(outfile_path)
    
    # Retrieve LinkedIn organisation id
    organisation_id = extract_organisation_id(url)

    # Read search keys from file or use the provided string
    search_keys = read_search_keys(search_key_input)

    # Call the linkedin_search function for each search key and get the results
    linkedin_search_list(search_keys, cookie_li_at, organisation_id, outfile_path)

        
