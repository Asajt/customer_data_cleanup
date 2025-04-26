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

def correct_names(first_name, last_name, detected_first_name_errors, detected_last_name_errors):
    """
    Corrects first and last names based on detected errors.

    This function takes individual first and last names along with the respective detected error sets and
    applies corrections based on predefined rules and configurations. It returns the corrected names
    along with updated error sets.

    Args:
        first_name (str): The first name to be corrected.
        last_name (str): The last name to be corrected.
        detected_first_name_errors (set): A set of detected error codes for the first name.
        detected_last_name_errors (set): A set of detected error codes for the last name.
        
    Returns:
        dict: A dictionary containing the following keys:
            - corrected_first_name (str or None): The corrected first name, or None if no correction was made.
            - corrected_first_name_errors (list): A sorted list of corrected error codes for the first name.
            - uncorrected_first_name_errors (list): A sorted list of uncorrected error codes for the first name.
            - corrected_last_name (str or None): The corrected last name, or None if no correction was made.
            - corrected_last_name_errors (list): A sorted list of corrected error codes for the last name.
            - uncorrected_last_name_errors (list): A sorted list of uncorrected error codes for the last name.
    """
    # 01. Store the original address components for comparison purposes
    original_first_name = first_name
    original_last_name = last_name
    
    # 02. Check for NaN values and convert them to empty strings
    first_name = "" if pd.isna(first_name) else str(first_name)
    last_name = "" if pd.isna(last_name) else str(last_name)
    
    corrected_first_name_errors = set()  
    uncorrected_first_name_errors = detected_first_name_errors.copy()
    
    corrected_last_name_errors = set()  
    uncorrected_last_name_errors = detected_last_name_errors.copy()
    
    corrected_first_name = first_name
    corrected_last_name = last_name
    
    # First name corrections 
    if detected_first_name_errors:
        # missing data 
        if should_correct('1101', error_config):
            if '1101' in detected_first_name_errors:
                corrected_first_name_before = corrected_first_name
                corrected_first_name = None
                if corrected_first_name_before != corrected_first_name:
                    corrected_first_name_errors.add('1101')
                    uncorrected_first_name_errors.remove('1101')

        # unnecessary spaces
        if should_correct('1102', error_config):
            if '1102' in detected_first_name_errors: 
                corrected_first_name_before = corrected_first_name
                corrected_first_name = corrected_first_name.rstrip() # removes trailing whitespaces
                corrected_first_name = corrected_first_name.lstrip() # removes leading whitespaces
                corrected_first_name = re.sub(r'\s{2,}', ' ', corrected_first_name) # removes double whitespace
                corrected_first_name = re.sub(r'\s,', ',', corrected_first_name) # removes whitespaces before comma
                if corrected_first_name_before != corrected_first_name:
                    corrected_first_name_errors.add('1102')
                    uncorrected_first_name_errors.remove('1102')
            
        # formatting issues - has to be in title case
        if should_correct('1104', error_config):
            if '1104' in detected_first_name_errors:
                corrected_first_name_before = corrected_first_name
                # Split the string into parts
                first_name_parts = first_name.replace(',', '').split()
                # List to keep track of items already added (in lowercase for comparison)
                seen = set()
                # List for the result, preserving original case
                first_name_title_case_parts = []
                for part in first_name_parts:
                    # Convert part to lowercase for case-insensitive comparison
                    if part.upper() not in seen:
                        seen.add(part.upper())
                        # Capitalize the first letter and make the rest lowercase
                        first_name_title_case_parts.append(part.capitalize())
                # Join the unique parts back together
                corrected_first_name = ' '.join(first_name_title_case_parts)
                if corrected_first_name_before != corrected_first_name:
                    corrected_first_name_errors.add('1104')
                    uncorrected_first_name_errors.remove('1104')
                              
        #consecutive duplicates detected
        if should_correct('1105', error_config):
            if '1105' in detected_first_name_errors: 
                corrected_first_name_before = corrected_first_name
                # Split the string into parts
                first_name_parts = first_name.replace(',', '').split()
                # List to keep track of items already added (in lowercase for comparison)
                seen = set()
                # List for the result, preserving original case
                first_name_unique_parts = []
                for part in first_name_parts:
                    # Convert part to lowercase for case-insensitive comparison
                    if part.upper() not in seen:
                        seen.add(part.upper())  # Add upper version to seen for comparison
                        first_name_unique_parts.append(part)  # Add original part to result
                # Join the unique parts back together
                corrected_first_name = ' '.join(first_name_unique_parts)
                if corrected_first_name_before != corrected_first_name:
                    corrected_first_name_errors.add('1105')
                    uncorrected_first_name_errors.remove('1105')

    # Last name corrections 
    if detected_last_name_errors:
        # missing data 
        if should_correct('1201', error_config):
            if '1201' in detected_last_name_errors: 
                corrected_last_name_before = corrected_last_name
                corrected_last_name = None
                if corrected_last_name_before != corrected_last_name:
                    corrected_last_name_errors.add('1201')
                    uncorrected_last_name_errors.remove('1201')
            
        # Street number error: unnecessary spaces
        if should_correct('1202', error_config):
            if '1202' in detected_last_name_errors: 
                corrected_last_name_before = corrected_last_name
                corrected_last_name = corrected_last_name.rstrip() # removes trailing whitespaces
                corrected_last_name = corrected_last_name.lstrip() # removes leading whitespaces
                corrected_last_name = re.sub(r'\s{2,}', ' ', corrected_last_name) # removes double whitespace
                corrected_last_name = re.sub(r'\s,', ',', corrected_last_name) # removes whitespaces before comma
                if corrected_last_name_before != corrected_last_name:
                    corrected_last_name_errors.add('1202')
                    uncorrected_last_name_errors.remove('1202')

        # formatting issues - has to be in title case
        if should_correct('1204', error_config):
            if '1204' in detected_last_name_errors:
                corrected_last_name_before = corrected_last_name
                # Split the string into parts
                last_name_parts = last_name.replace(',', '').split()
                # List to keep track of items already added (in lowercase for comparison)
                seen = set()
                # List for the result, preserving original case
                last_name_title_case_parts = []
                for part in last_name_parts:
                    # Convert part to lowercase for case-insensitive comparison
                    if part.upper() not in seen:
                        seen.add(part.upper())
                        # Capitalize the first letter and make the rest lowercase
                        last_name_title_case_parts.append(part.capitalize())
                # Join the unique parts back together
                corrected_last_name = ' '.join(last_name_title_case_parts)
                if corrected_last_name_before != corrected_first_name:
                    corrected_last_name_errors.add('1204')
                    uncorrected_last_name_errors.remove('1204')
        
        #consecutive duplicates detected
        if should_correct('1205', error_config):
            if '1205' in detected_last_name_errors: 
                corrected_last_name_before = corrected_last_name
                # Split the string into parts
                last_name_parts = last_name.replace(',', '').split()
                # List to keep track of items already added (in lowercase for comparison)
                seen = set()
                # List for the result, preserving original case
                last_name_unique_parts = []
                for part in last_name_parts:
                    # Convert part to lowercase for case-insensitive comparison
                    if part.upper() not in seen:
                        seen.add(part.upper())  # Add upper version to seen for comparison
                        last_name_unique_parts.append(part)  # Add original part to result
                # Join the unique parts back together
                corrected_last_name = ' '.join(last_name_unique_parts)
                if corrected_last_name_before != corrected_last_name:
                    corrected_last_name_errors.add('1205')
                    uncorrected_last_name_errors.remove('1205')
                    
    return {
    "corrected_first_name": corrected_first_name if corrected_first_name != original_first_name else None,
    "corrected_first_name_errors": sorted(corrected_first_name_errors),
    "uncorrected_first_name_errors": sorted(uncorrected_first_name_errors),

    "corrected_last_name": corrected_last_name if corrected_last_name != original_last_name else None,
    "corrected_last_name_errors": sorted(corrected_last_name_errors),
    "uncorrected_last_name_errors": sorted(uncorrected_last_name_errors),
    }    

if __name__ == "__main__":

    # TESTING

    customer_data = "src/processed_data/02_detected_name_errors.xlsx"

    df = pd.read_excel(customer_data)
    
    # split the string into a set for processing
    df['name_detected_errors'] = df['name_detected_errors'].apply(split_into_set)
    df['surname_detected_errors'] = df['surname_detected_errors'].apply(split_into_set)
    
    # Apply the correction function to each row
    df_new = df.apply(lambda row: pd.Series(correct_names( 
        first_name=row['FIRST_NAME'],
        last_name=row['LAST_NAME'],
        detected_first_name_errors=row["name_detected_errors"],
        detected_last_name_errors=row["surname_detected_errors"],
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
        "FIRST_NAME", 
            "corrected_first_name", 
            "name_detected_errors", 
            "corrected_first_name_errors", 
            "uncorrected_first_name_errors",
        "LAST_NAME", 
            "corrected_last_name", 
            "surname_detected_errors", 
            "corrected_last_name_errors", 
            "uncorrected_last_name_errors",
    ]
    
    # Save to Excel
    final_df[columns_to_export].to_excel("src/processed_data/03_corrected_name_errors.xlsx", index=False)
    
    print("✅ Correction of name errors completed and saved.")