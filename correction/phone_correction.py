import pandas as pd
import re
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.errors_utils import should_correct, load_error_config

error_config = load_error_config()

def split_into_set(detected_errors_column):
    """
    Converts the input into a set of strings, handling various input types.

    Parameters:
    detected_errors_column (str, float, int, set, list, or None): The input data to be converted into a set.
        - If the input is a string, it is split by commas, stripped of whitespace, and empty strings are excluded.
        - If the input is a float or int, it is converted to a string and added to the set.
        - If the input is a set or list, each element is converted to a string, stripped of whitespace, and empty strings are excluded.
        - If the input is None or NaN, an empty set is returned.

    Returns:
    set: A set of strings derived from the input data.
    """
    if pd.isna(detected_errors_column):
        return set()
    if isinstance(detected_errors_column, str):
        # Split by comma, strip each item, exclude empty strings
        return set(code.strip() for code in detected_errors_column.split(",") if code.strip())
    elif isinstance(detected_errors_column, (float, int)):
        return {str(int(detected_errors_column))}
    elif isinstance(detected_errors_column, (set, list)):
        return set(str(code).strip() for code in detected_errors_column if str(code).strip())
    else:
        return set()

def correct_phone(phone: str, detected_phone_errors: set) -> dict:
    """
    Corrects phone number based on detected errors.

    This function takes individual phone number along with the respective detected error set and
    applies corrections based on predefined rules and configurations. It returns the corrected phone
    number along with updated error set.

    Args:
        phone (str): The phone number to be corrected.
        detected_phone_errors (set): A set of detected error codes for the phone number.
        
    Returns:
        dict: A dictionary containing the following keys:
            - corrected_phone (str or None): The corrected phone number, or None if no correction was made.
            - corrected_phone_errors (list): A sorted list of corrected error codes for the phone number.
            - uncorrected_phone_errors (list): A sorted list of uncorrected error codes for the phone number.
    """
    
    # 01. Store the original address components for comparison purposes
    original_phone = phone
    
    # 02. Check for NaN values and convert them to empty strings
    phone = "" if pd.isna(phone) else str(phone)
    
    corrected_phone_errors = set()  
    uncorrected_phone_errors = detected_phone_errors.copy()
    
    corrected_phone = phone
    
    # First name corrections 
    if detected_phone_errors:
        # missing data 
        if should_correct('3101', error_config):
            if '3101' in detected_phone_errors:
                corrected_phone_before = corrected_phone
                corrected_phone = None
                if corrected_phone_before != corrected_phone:
                    corrected_phone_errors.add('3101')
                    uncorrected_phone_errors.remove('3101')

        # unnecessary spaces
        if should_correct('3102', error_config):
            if '3102' in detected_phone_errors: 
                corrected_phone_before = corrected_phone
                corrected_phone = corrected_phone.rstrip() # removes trailing whitespaces
                corrected_phone = corrected_phone.lstrip() # removes leading whitespaces
                corrected_phone = re.sub(r'\s{2,}', ' ', corrected_phone) # removes double whitespace
                corrected_phone = re.sub(r'\s,', ',', corrected_phone) # removes whitespaces before comma
                if corrected_phone_before != corrected_phone:
                    corrected_phone_errors.add('3102')
                    uncorrected_phone_errors.remove('3102')
                    
        # 3103	Invalid characters        
        if should_correct('3103', error_config):
            if '3103' in detected_phone_errors: 
                corrected_phone_before = corrected_phone
                corrected_phone = re.sub(r"^\+386", "00386", corrected_phone)
                corrected_phone = re.sub(r"^\+00386", "00386", corrected_phone)
                corrected_phone = corrected_phone.replace(" ", "")
                corrected_phone = corrected_phone.replace("/", "")
                corrected_phone = corrected_phone.replace("-", "")
                if corrected_phone_before != corrected_phone:
                    corrected_phone_errors.add('3103')
                    uncorrected_phone_errors.remove('3103')
                
        # 3104	Formatting Issue
        if should_correct('3104', error_config):
            if '3104' in detected_phone_errors:
                mobile_prefixes = ("041", "031", "051", "040", "030", "01", "068", "069", "065", "070", "071")
                if corrected_phone.startswith(mobile_prefixes):
                    corrected_phone_before = corrected_phone
                    corrected_phone = re.sub(r"^0", "00386", corrected_phone)
                    if corrected_phone_before != corrected_phone:
                        corrected_phone_errors.add('3104')
                        uncorrected_phone_errors.remove('3104')
                      
    return (
    corrected_phone if corrected_phone != original_phone else None,
    sorted(corrected_phone_errors),
    sorted(uncorrected_phone_errors),
    )    

if __name__ == "__main__":

    # TESTING

    customer_data = "src/processed_data/02_detected_phone_errors.xlsx"

    df = pd.read_excel(customer_data)
    
    # split the string into a set
    df['phone_detected_errors'] = df['phone_detected_errors'].apply(split_into_set)

    df[["corrected_phone", "corrected_phone_errors", "uncorrected_phone_errors"]] = df.apply(
        lambda row: pd.Series(correct_phone(
            phone=row['PHONE_NUMBER'],
            detected_phone_errors=row["phone_detected_errors"],
        )), axis=1
    )
        
    # Convert lists and sets to strings before saving
    for col in df.columns:
        if "errors" in col:
            df[col] = df[col].apply(
                lambda x: ", ".join(sorted(x)) if isinstance(x, (set, list)) else x
            )
    
    # Optional: Filter columns to save
    columns_to_export = [
        "CUSTOMER_ID",  #
        "PHONE_NUMBER", 
            "corrected_phone", 
            "phone_detected_errors", 
            "corrected_phone_errors", 
            "uncorrected_phone_errors"
    ]
    
    # Save to Excel
    df[columns_to_export].to_excel("src/processed_data/03_corrected_phone_errors.xlsx", index=False)
    
    print("✅ Correction of phone errors completed and saved.")