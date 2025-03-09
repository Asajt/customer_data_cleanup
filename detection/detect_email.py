import re
import pandas as pd
import string
from email_validator import validate_email, EmailNotValidError

def detect_email_errors(email):
    # Check for NaN values and convert them to empty strings
    email = "" if pd.isna(email) else str(email)

    distinct_detected_errors = set()
    
    error_messages = {
        '2101': 'EMAIL: Missing Data',
        '2102': 'EMAIL: Unnecessary Spaces',
        '2103': 'EMAIL: Invalid Characters',
        '2104': 'EMAIL: Formatting Issue',
        '2105': 'EMAIL: Possibly Two Emails',
        '2106': 'EMAIL: Invalid domain',
        '2107': 'EMAIL: Possibly Invalid Domain',
        '2108': 'EMAIL: Undetected Email Error'
    }
    
    errors = []  # List to store errors for this iteration
    
    # 2101 Check for missing data
    if pd.isna(email) or email is None or email.strip() == "" or email.strip() == "/" :
            errors.append('2101') 
            distinct_detected_errors.add('2101')   
    else:
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            # 2102 Check for unnecessary spaces
            if email.startswith(' ') or email.endswith(' ') or "  " in email:
                errors.append('2102')
                distinct_detected_errors.add('2102')
            # 2103 Check for invalid characters
            if not re.search(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
                errors.append('2103')
                distinct_detected_errors.add('2103')
            # 2104 Check for formatting issues
            if (
                not email.isascii()  # Ensure only ASCII characters are used
                or email.count('@') != 1  # Only one "@" symbol is allowed
                or email.startswith('@') or email.endswith('@')  # "@" cannot be at the start or end
                or email.split('@')[0] == ""  # Missing local part (before @)
                or email.split('@')[-1].count('.') == 0  # Missing "." in domain
                or email.split('@')[-1].startswith('.') or email.split('@')[-1].endswith('.')  # "." cannot be at start or end of domain
                or any(char.isspace() for char in email)  # No spaces allowed
            ):
                errors.append('2104')
                distinct_detected_errors.add('2104')
            # 2105 Check for two emails 
            if (
                len(email) > 1 
                or email.count('@') > 1 
                or email.count('.') > 1 
                or email.count(',') > 1 
                or email.count(' ') > 1 
                or email.count(';') > 1
            ):
                errors.append('2105')
                distinct_detected_errors.add('2105')
            # 2106 Check for invalid domain
            domain = email.split('@')[-1]
            if not re.search(r'^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', domain):
                errors.append('2106')
                distinct_detected_errors.add('2106')
            else:
            # 2107 Check for possibly invalid domain
                valid_domains = [
                    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
                    'siol.net', 't-2.net', 'amis.net', 'email.si', 'gov.si', 
                    'guest.arnes.si', 'guest.arnes.net','guest.arnes.org'
                ]
                if domain not in valid_domains:
                    errors.append('2107')
                    distinct_detected_errors.add('2107')
            # 2108 If no specific error found, add undetected email error
            if not errors:
                errors.append('2108')
                distinct_detected_errors.add('2108')
        
    return ','.join(sorted(distinct_detected_errors))