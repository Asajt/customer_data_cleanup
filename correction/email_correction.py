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

def correct_email(email, detected_email_errors):
    """
    Corrects email based on detected errors.

    This function takes individual email address along with the respective detected error set and 
    applies corrections based on predefined rules and configurations. It returns the corrected email
    address along with updated error set.

    Args:
        email (str): The email address to be corrected.
        detected_email_errors (set): A set of detected error codes for the email address.

    Returns:
        dict: A dictionary containing the following keys:
            - corrected_email (str or None): The corrected email address, or None if no correction was made.
            - corrected_email_errors (list): A sorted list of corrected error codes for the email address.
            - uncorrected_email_errors (list): A sorted list of uncorrected error codes for the email address.
    """
    
    # 01. Store the original address components for comparison purposes
    original_email = email
    
    # 02. Check for NaN values and convert them to empty strings
    email = "" if pd.isna(email) else str(email)
    
    corrected_email_errors = set()  
    uncorrected_email_errors = detected_email_errors.copy()
    
    corrected_email = email
    
    # First name corrections 
    if detected_email_errors:
        # missing data 
        if should_correct('2101', error_config):
            if '2101' in detected_email_errors:
                corrected_email_before = corrected_email
                corrected_email = None
                if corrected_email_before != corrected_email:
                    corrected_email_errors.add('2101')
                    uncorrected_email_errors.remove('2101')

        # unnecessary spaces
        if should_correct('2102', error_config):
            if '2102' in detected_email_errors: 
                corrected_email_before = corrected_email
                corrected_email = corrected_email.rstrip() # removes trailing whitespaces
                corrected_email = corrected_email.lstrip() # removes leading whitespaces
                corrected_email = re.sub(r'\s{2,}', ' ', corrected_email) # removes double whitespace
                corrected_email = re.sub(r'\s,', ',', corrected_email) # removes whitespaces before comma
                if corrected_email_before != corrected_email:
                    corrected_email_errors.add('2102')
                    uncorrected_email_errors.remove('2102')
                    
    return {
    "corrected_email": corrected_email if corrected_email != original_email else None,
    "corrected_email_errors": sorted(corrected_email_errors),
    "uncorrected_email_errors": sorted(uncorrected_email_errors),
    }    

if __name__ == "__main__":

    # TESTING

    customer_data = "src/processed_data/02_detected_email_errors.xlsx"

    df = pd.read_excel(customer_data)
    
    # split the string into a set
    df['email_detected_errors'] = df['email_detected_errors'].apply(split_into_set)

    df_new = df.apply(lambda row: pd.Series(correct_email( 
        email=row['EMAIL'],
        detected_email_errors=row["email_detected_errors"],
    )), axis=1)
    
    # Merge original and corrected data
    final_df = pd.concat([df, df_new], axis=1)
    
    # Convert lists and sets to strings before saving
    for col in final_df.columns:
        if "errors" in col:
            final_df[col] = final_df[col].apply(
                lambda x: ", ".join(sorted(x)) if isinstance(x, (set, list)) else x
            )
    
    # Optional: Filter columns to save
    columns_to_export = [
        "CUSTOMER_ID",  #
        "EMAIL", 
            "corrected_email", 
            "email_detected_errors", 
            "corrected_email_errors", 
            "uncorrected_email_errors"
    ]
    
    # Save to Excel
    final_df[columns_to_export].to_excel("src/processed_data/03_corrected_email_errors.xlsx", index=False)
    
    print("✅ Correction of email errors completed and saved.")