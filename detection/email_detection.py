import re
import pandas as pd
from email_validator import validate_email, EmailNotValidError

def detect_email_errors(email):
    # Ensure it's a valid string
    email = "" if pd.isna(email) else str(email)

    email_errors = set()

    # Error messages for each error ID
    error_messages = {
        '2101': 'EMAIL: Missing Data',
        '2102': 'EMAIL: Unnecessary Spaces',
        '2103': 'EMAIL: Invalid Characters',
        '2104': 'EMAIL: Formatting Issue',
        '2105': 'EMAIL: Possibly Two Emails',
        '2106': 'EMAIL: Invalid domain',
        '2107': 'EMAIL: Possibly Invalid Domain',
        '2000': 'EMAIL: Undetected Email Error'
    }

    # Check for missing data (2101)
    if email.strip() == "" or email.strip() == "/" :
        email_errors.add('2101')

    else:
        # Check for unnecessary spaces (2102)
        if email.startswith(' ') or email.endswith(' ') or "  " in email:
            email_errors.add('2102')

        # Check for invalid characters (2103)
        if not re.search(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            email_errors.add('2103')

        # Check for formatting issues (2104)
        if (
            not email.isascii()  # Ensure only ASCII characters are used
            or email.count('@') != 1  # Only one "@" symbol is allowed
            or email.startswith('@') or email.endswith('@')  # "@" cannot be at the start or end
            or email.split('@')[0] == ""  # Missing local part (before @)
            or email.split('@')[-1].count('.') == 0  # Missing "." in domain
            or email.split('@')[-1].startswith('.') or email.split('@')[-1].endswith('.')  # "." cannot be at start or end of domain
            or any(char.isspace() for char in email)  # No spaces allowed
        ):
            email_errors.add('2104')

        # Check for possibly two emails (2105)
        if (
            email.count('@') > 1 
            or email.count(',') > 1 
            or email.count(' ') > 1 
            or email.count(';') > 1
        ):
            email_errors.add('2105')

        # Check for invalid domain (2106)
        domain = email.split('@')[-1]
        if not re.search(r'^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', domain):
            email_errors.add('2106')

        else:
            # Check for possibly invalid domain (2107)
            valid_domains = [
                'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
                'siol.net', 't-2.net', 'amis.net', 'email.si', 'gov.si', 
                'guest.arnes.si', 'guest.arnes.net', 'guest.arnes.org', 
                'icloud.com'
            ]
            if domain not in valid_domains:
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