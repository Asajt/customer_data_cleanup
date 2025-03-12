import re
import pandas as pd

def detect_phone_errors(email):
    # Check for NaN values and convert them to empty strings
    phone = "" if pd.isna(phone) else str(phone)

    errors = set()
    
    error_messages = {
        '3101': 'PHONE: Missing Data',
        '3102': 'PHONE: Unnecessary Spaces',
        '3103': 'PHONE: Invalid characters',
        '3104': 'PHONE: Formatting Issue',
        '3105': 'PHONE: Too many digits',
        '3106': 'PHONE: Too little digits',
        '3107': 'PHONE: Two phone numbers',
        '3108': 'PHONE: Different country format'
    }
        
    # 3101 Check for missing data
    if pd.isna(phone) or phone is None or phone.strip() == "" or phone.strip() == "/" :
        errors.add('3101') 
    else:
        # 3102 Check for unnecessary spaces
        if phone.startswith(' ') or phone.endswith(' ') or "  " in phone:
            errors.add('3102')
        # 3105 Check for too many digits
        if len(phone) > 13:
            errors.add('3105')
        # 3106 Check for too little digits
        if len(phone) < 13:
            errors.add('3106')
        # 3104 Check for formatting issues
        if (
            phone.count('+') > 1  # Only one "+" symbol is allowed
            or phone.startswith('+')  # "+" has to be at the start
            or any(char.isspace() for char in phone)  # No spaces allowed
        ):
            errors.add('3104')
        
        # 3103 Check for invalid characters
        if not re.search(r'^[0-9]+$', phone):
            errors.add('3103')
            
        # 3107 Check for two phone numbers
        if (
            len(phone) > 1
            or phone.count('+') > 1
            or phone.count(',') > 1
            or phone.count(' ') > 1
            or phone.count(';') > 1
        ):
            errors.add('3107')
        # 3108 Check for different country format
        if phone.startswith('00'):
            errors.add('3108')
        
    return ','.join(sorted(errors))