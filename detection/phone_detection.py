import re
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.errors_utils import should_detect, load_error_config

error_config = load_error_config()

def detect_phone_errors(phone: str) -> set:
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
    
    # 3101 Check for missing data
    rule_condition = phone.strip() == "" or phone.strip() == "x" or not re.search(r"[a-zA-Z0-9]", phone)
    if should_detect('3101', error_config):
        if rule_condition:
            phone_errors.add('3101')
        else:
            # 3102 Check for unnecessary spaces
            rule_condition = (phone.startswith(' ') or phone.endswith(' ') or "  " in phone)
            if should_detect('3102', error_config):
                if rule_condition:
                    phone_errors.add('3102')
            
            # 3107 Check for two phone numbers
            rule_condition = (len(re.findall(r"\d{6,}", phone)) > 1
                              or re.search(",", phone)
                              or re.search(";", phone)
                            )
            if should_detect('3107', error_config):
                if rule_condition:
                    phone_errors.add('3107')
            
            # 3103 Check for invalid characters
            skip_if_condition = not '3107' in phone_errors
            rule_condition = not phone.replace("  ", "").strip().isdigit() # anything that is non-digit is flagged, except blankspaces since this is handled in error 3102
            if should_detect('3103', error_config):
                if skip_if_condition:
                    if rule_condition:
                        phone_errors.add('3103')
                    
            # 3105 Check for too many digits      
            skip_if_condition = not '3107' in phone_errors              
            digit_count = len(re.findall(r"\d", phone))
            if phone.strip().startswith("00386"):
                rule_condition = digit_count > 13
            elif phone.strip().startswith("386"):
                rule_condition = digit_count > 11
            elif phone.strip().startswith("+00386"):
                rule_condition = digit_count > 13
            elif phone.strip().startswith("0"):
                rule_condition = digit_count > 9
            elif phone.strip().startswith("+386"):
                rule_condition = digit_count > 11
            else:
                rule_condition = digit_count > 14  # fallback for unexpected cases
            if should_detect("3105", error_config):
                if skip_if_condition:
                    if rule_condition:
                        phone_errors.add("3105")
                    
            # 3106 Check for too little digits
            digit_count = len(re.findall(r"\d", phone))
            if phone.strip().startswith("00386"):
                rule_condition = digit_count < 13
            elif phone.strip().startswith("386"):
                rule_condition = digit_count < 11
            elif phone.strip().startswith("+00386"):
                rule_condition = digit_count < 13
            elif phone.strip().startswith("0"):
                rule_condition = digit_count < 9
            elif phone.strip().startswith("+386"):
                rule_condition = digit_count < 11
            else:
                rule_condition = digit_count < 9  # fallback for unexpected cases
            if should_detect("3106", error_config):
                if rule_condition:
                    phone_errors.add("3106")
            
            # 3104 Check for formatting issues
            skip_if_condition = not phone_errors
            rule_condition = (not re.search(r'^00386[1-7][0-9]{7}$', phone.strip()) or
                              not phone.strip()
                              )
            if should_detect('3104', error_config):
                if skip_if_condition:
                    if rule_condition:
                        phone_errors.add('3104')
        
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

