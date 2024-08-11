# linkedin-enum

A Python script to retrieve a user's current job title from LinkedIn profiles based on provided names and a LinkedIn organization URL.

USE RESPONSIBLY AND AT YOUR OWN RISK! Throwaway accounts only or risk getting banned.

## Prerequisites
Python 3.x

## Usage

`python3 linkedin-enum.py --search <search_key_or_file> --country <country_value> --outfile <csv_outfile> --cookie <li_at_cookie_value> --companyurl <linkedin_company_url>`

- <linkedin_company_url>: LinkedIn organization URL, e.g. https://www.linkedin.com/company/google/
- <search_key_or_file>: Name to search or path to a text file containing multiple names (one per line).
- <country_value>: country filter for user search
- <li_at_cookie_value>: li_at cookie value obtained from a valid LinkedIn session.
- <csv_outfile>: Path to the output CSV file.

Example:

`python3 linkedin-enum.py --search ./target_names.txt --country hongkong --outfile role_enum.csv --cookie li_at_cookie --companyurl https://www.linkedin.com/company/google/`

## Notes
- Make sure to comply with LinkedIn's terms of service while using this script.
- Keep in mind that the script might not operate stealthily, and the target user might be notified of profile views. Consider reviewing your privacy settings on LinkedIn where necessary.
- IMPORTANT: Run this script responsibly and avoid making too many requests in a short period. Otherwise your account might get blocked by LinkedIn and you'll have to send in a request to reverse it.
