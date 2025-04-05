import re
import pandas as pd

def detect_phone_errors(phone):
    """Detects errors in phone numbers based on various criteria.

    This function checks for missing data, unnecessary spaces, invalid characters,
    formatting issues, duplicates, and the presence of multiple phone numbers in a single field.

    Args:
        phone (str): The phone number to be checked.

    Returns:
        set: A set containing detected error codes for the phone number.
    """
    # Check for NaN values and convert them to empty strings
    phone = "" if pd.isna(phone) else str(phone)

    phone_errors = set()
    
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
        phone_errors.add('3101') 
    else:
        # 3102 Check for unnecessary spaces
        if phone.startswith(' ') or phone.endswith(' ') or "  " in phone:
            phone_errors.add('3102')
        # 3105 Check for too many digits
        if len(phone) > 13:
            phone_errors.add('3105')
        # 3106 Check for too little digits
        if len(phone) < 13:
            phone_errors.add('3106')
        # 3104 Check for formatting issues
        if (
            phone.count('+') > 1  # Only one "+" symbol is allowed
            or phone.startswith('+')  # "+" has to be at the start
            or any(char.isspace() for char in phone)  # No spaces allowed
        ):
            phone_errors.add('3104')
        
        # 3103 Check for invalid characters
        if not re.search(r'^[0-9]+$', phone):
            phone_errors.add('3103')
            
        # 3107 Check for two phone numbers
        if (
            phone.count('+') > 1
            or phone.count(',') > 1
            or phone.count(' ') > 1
            or phone.count(';') > 1
        ):
            phone_errors.add('3107')
        # 3108 Check for different country format
        if not phone.startswith('00386'):
            phone_errors.add('3108')
        
    return phone_errors

if __name__ == "__main__":
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"

    df = pd.read_excel(customer_data)

    df["phone_detected_errors"] = df["PHONE_NUMBER"].apply(detect_phone_errors)
    
    # Convert the set of errors to a sorted list
    df["phone_detected_errors"] = df["phone_detected_errors"].apply(lambda x: ", ".join(sorted(x)))

    # choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", 
        "PHONE_NUMBER", "phone_detected_errors"
    ]
    df = df[columns_to_keep]
    
    # Save the result
    df.to_excel("src/processed_data/02_detected_phone_errors.xlsx", index=False)
    print("Detection of phone errors completed and saved!")

