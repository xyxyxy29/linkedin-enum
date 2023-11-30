# linkedin-enum

A Python script to retrieve a user's current job title from LinkedIn profiles based on provided names and a LinkedIn organization URL.

## Prerequisites
Python 3.x

## Usage

`python script.py <linkedin_company_url> <search_key_or_file> <li_at_cookie_value> <csv_outfile>`

- <linkedin_company_url>: LinkedIn organization URL, e.g. https://www.linkedin.com/company/google/
- <search_key_or_file>: Name to search or path to a text file containing multiple names (one per line).
- <li_at_cookie_value>: li_at cookie value obtained from a valid LinkedIn session.
- <csv_outfile>: Path to the output CSV file.

Example:

`python script.py https://www.linkedin.com/company/example search_keys.txt LI_AT_COOKIE_VALUE output.csv`

## Notes
- Make sure to comply with LinkedIn's terms of service while using this script.
- Keep in mind that the script might not operate stealthily, and the target user might be notified of profile views. Consider reviewing your privacy settings on LinkedIn where necessary.
- IMPORTANT: Run this script responsibly and avoid making too many requests in a short period. Otherwise your account might get blocked by LinkedIn and you'll have to send in a request to reverse it.
