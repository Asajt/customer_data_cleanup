import re
import pandas as pd
from email_validator import validate_email, EmailNotValidError
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.errors_utils import should_detect, load_error_config

error_config = load_error_config()

def detect_email_errors(email):
    """Detects errors in email addresses based on various criteria.

    This function checks for missing data, unnecessary spaces, invalid characters,
    formatting issues, duplicates, and the presence of multiple emails in a single field.

    Args:
        email (str): The email address to be checked.

    Returns:
        set: A set containing detected error codes for the email address.
    """
    
    # Ensure it's a valid string
    email = "" if pd.isna(email) else str(email)

    email_errors = set()

    # Check for missing data (2101)
    rule_condition = email.strip() == ""
    if should_detect('2101', error_config):
        if rule_condition:
            email_errors.add('2101')

        else:
            # Check for unnecessary spaces (2102)
            rule_condition = (email.startswith(' ') or email.endswith(' ') or "  " in email)
            if should_detect('2102', error_config):
                if rule_condition:
                    email_errors.add('2102')

            # Check for invalid characters (2103)
            rule_condition = (not re.search(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email))
            if should_detect('2103', error_config):
                if rule_condition:
                    email_errors.add('2103')

            # Check for formatting issues (2104)
            rule_condition = (
                    not email.isascii()  # Ensure only ASCII characters are used
                    or email.count('@') != 1  # Only one "@" symbol is allowed
                    or email.startswith('@') or email.endswith('@')  # "@" cannot be at the start or end
                    or email.split('@')[0] == ""  # Missing local part (before @)
                    or email.split('@')[-1].count('.') == 0  # Missing "." in domain
                    or email.split('@')[-1].startswith('.') or email.split('@')[-1].endswith('.')  # "." cannot be at start or end of domain
                    or any(char.isspace() for char in email))  # No spaces allowed
            if should_detect('2104', error_config):
                if rule_condition:
                    email_errors.add('2104')

            # Check for possibly two emails (2105)
            rule_condition = (
                    email.count('@') > 1 
                    or email.count(',') > 1 
                    or email.count(' ') > 1 
                    or email.count(';') > 1)
            if should_detect('2105', error_config):
                if rule_condition:
                    email_errors.add('2105')

            # Check for invalid domain (2106)
            domain = email.split('@')[-1]
            rule_condition = (not re.search(r'^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', domain))
            if should_detect('2106', error_config):
                if rule_condition:
                    email_errors.add('2106')

                else:
                    # Check for possibly invalid domain (2107)
                    valid_domains = [
                        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
                        'siol.net', 't-2.net', 'amis.net', 'email.si', 'gov.si', 
                        'guest.arnes.si', 'guest.arnes.net', 'guest.arnes.org', 
                        'icloud.com'
                    ]
                    rule_condition = (domain not in valid_domains)
                    if should_detect('2107', error_config):
                        if rule_condition:
                            email_errors.add('2107')

            # If no specific error found, try validating the email format (2000)
            if not email_errors:
                try:
                    validate_email(email, check_deliverability=False)
                except EmailNotValidError:
                    email_errors.add('2000')

    # return ','.join(sorted(email_errors
    return email_errors


if __name__ == "__main__":
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"

    df = pd.read_excel(customer_data)

    df["email_detected_errors"] = df["EMAIL"].apply(detect_email_errors)
    
    # Convert the set of errors to a sorted list
    df["email_detected_errors"] = df["email_detected_errors"].apply(lambda x: ", ".join(sorted(x)))

    # choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", 
        "EMAIL", "email_detected_errors"
    ]
    df = df[columns_to_keep]
    
    # Save the result
    df.to_excel("src/processed_data/02_detected_email_errors.xlsx", index=False)
    print("Detection of email errors completed and saved!")