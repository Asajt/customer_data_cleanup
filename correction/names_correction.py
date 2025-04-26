import pandas as pd
import re
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.errors_utils import should_correct, load_error_config

error_config = load_error_config()

def split_into_set(detected_errors_column):
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
    
    # 01. Store the original address components for comparison purposes
    original_first_name = first_name
    original_last_name = last_name
    
    # 02. Check for NaN values and convert them to empty strings
    first_name = "" if pd.isna(first_name) else str(first_name)
    last_name = "" if pd.isna(last_name) else str(last_name)
    
    # 3 split the string into a set
    detected_first_name_errors = split_into_set(detected_first_name_errors)
    detected_last_name_errors = split_into_set(detected_last_name_errors)
    
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
                corrected_street_before = corrected_street
                corrected_street = None
                if corrected_street_before != corrected_street:
                    corrected_street_errors.add('4101')
                    uncorrected_street_errors.remove('4101')
            
        # Street error: unnecessary spaces
        if should_correct('4102', error_config):
            if '4102' in detected_street_errors: 
                corrected_street_before = corrected_street
                corrected_street = corrected_street.rstrip() # removes trailing whitespaces
                corrected_street = corrected_street.lstrip() # removes leading whitespaces
                corrected_street = re.sub(r'\s{2,}', ' ', corrected_street) # removes double whitespace
                corrected_street = re.sub(r'\s,', ',', corrected_street) # removes whitespaces before comma
                if corrected_street_before != corrected_street:
                    corrected_street_errors.add('4102')
                    uncorrected_street_errors.remove('4102')
            
        # Street error: no space after full stop
        if should_correct('4108', error_config):
            if '4108' in detected_street_errors:
                corrected_street_before = corrected_street
                corrected_street = re.sub(r'\.(?![\s\W])', r'. ', corrected_street)
                if corrected_street_before != corrected_street:
                    corrected_street_errors.add('4108')
                    uncorrected_street_errors.remove('4108')
            
        # Street error: contains variation of BŠ
        if should_correct('4106', error_config):
            if '4106' in detected_street_errors:
                corrected_street_before = corrected_street
                for pattern in hn_patterns:
                    corrected_street = re.sub(pattern, '', corrected_street, flags=re.IGNORECASE)
                if corrected_street_before != corrected_street:
                    corrected_street_errors.add('4106')
                    uncorrected_street_errors.remove('4106')
                        
        # Street error: invalid abbreviations
        if should_correct('4107', error_config):
            if '4107' in detected_street_errors: 
                corrected_street_before = corrected_street
                corrected_street = corrected_street.replace('c.', 'cesta').replace('ce.', 'cesta').replace('C.', 'CESTA').replace('Ce.', 'Cesta').replace('CE.', 'CESTA')
                corrected_street = corrected_street.replace('u.','ulica').replace('ul.','ulica').replace('U.','ULICA').replace('Ul.','Ulica').replace('UL.','ULICA')
                if corrected_street_before != corrected_street:
                    corrected_street_errors.add('4107')
                    uncorrected_street_errors.remove('4107')
            
        #Street error: consecutive duplicates detected
        if should_correct('4110', error_config):
            if '4110' in detected_street_errors: 
                corrected_street_before = corrected_street
                # Split the string into parts
                street_parts = street.replace(',', '').split()
                # List to keep track of items already added (in lowercase for comparison)
                seen = set()
                # List for the result, preserving original case
                street_unique_parts = []
                for part in street_parts:
                    # Convert part to lowercase for case-insensitive comparison
                    if part.upper() not in seen:
                        seen.add(part.upper())  # Add upper version to seen for comparison
                        street_unique_parts.append(part)  # Add original part to result
                # Join the unique parts back together
                corrected_street = ' '.join(street_unique_parts)
                if corrected_street_before != corrected_street:
                    corrected_street_errors.add('4110')
                    uncorrected_street_errors.remove('4110')

    # Street number corrections 
    if detected_last_name_errors:
        # missing data 
        if should_correct('4201', error_config):
            if '4201' in detected_street_number_errors: 
                corrected_street_number_before = corrected_street_number
                corrected_street_number = None
                if corrected_street_number_before != corrected_street_number:
                    corrected_street_number_errors.add('4201')
                    uncorrected_street_number_errors.remove('4201')
            
        # Street number error: unnecessary spaces
        if should_correct('4202', error_config):
            if '4202' in detected_street_number_errors: 
                corrected_street_number_before = corrected_street_number
                corrected_street_number = corrected_street_number.rstrip() # removes trailing whitespaces
                corrected_street_number = corrected_street_number.lstrip() # removes leading whitespaces
                corrected_street_number = re.sub(r'\s{2,}', ' ', corrected_street_number) # removes double whitespace
                corrected_street_number = re.sub(r'\s,', ',', corrected_street_number) # removes whitespaces before comma
                if corrected_street_number_before != corrected_street_number:
                    corrected_street_number_errors.add('4202')
                    uncorrected_street_number_errors.remove('4202')
            
        # Street number error: contains variation of BŠ
        if should_correct('4203', error_config):
            if '4203' in detected_street_number_errors:
                corrected_street_number_before = corrected_street_number
                for pattern in hn_patterns:
                    corrected_street_number = re.sub(pattern, '', corrected_street_number, flags=re.IGNORECASE)
                if corrected_street_number_before != corrected_street_number:
                    corrected_street_number_errors.add('4203')
                    uncorrected_street_number_errors.remove('4203')
                    
        # remove leading 0s
        if should_correct('4206', error_config):
            if '4206' in detected_street_number_errors: 
                corrected_street_number_before = corrected_street_number
                corrected_street_number = corrected_street_number.lstrip('0')
                if corrected_street_number_before != corrected_street_number:
                    corrected_street_number_errors.add('4206')
                    uncorrected_street_number_errors.remove('4206')
            
        # remove dots
        if should_correct('4209', error_config):
            if '4209' in detected_street_number_errors:
                corrected_street_number_before = corrected_street_number
                corrected_street_number = corrected_street_number.rstrip('.')
                if corrected_street_number_before != corrected_street_number:
                    corrected_street_number_errors.add('4209')
                    uncorrected_street_number_errors.remove('4209')
            
        # correct spacing in between house number components
        skip_if_condition = not (any (code in detected_street_number_errors for code in ["4208", "4209"]))
        if should_correct('4205', error_config):
            if skip_if_condition:
                if '4205' in detected_street_number_errors:
                    corrected_street_number_before = corrected_street_number
                    corrected_street_number = re.sub(r'(\d+)(\/|(\s\/)|(\s\/\s)|\s|\.|\,|\-)([a-zA-ZččšžĆČŠŽ]{1,2})$', r'\1\5', corrected_street_number)
                    if corrected_street_number_before != corrected_street_number:
                        corrected_street_number_errors.add('4205')
                        uncorrected_street_number_errors.remove('4205')
                
        # street number error: invalid spacing between house number components    
        skip_if_condition = not '4208' in detected_street_number_errors
        if should_correct('4207', error_config):
            if skip_if_condition:
                if '4207' in detected_street_number_errors:
                    corrected_street_number_before = corrected_street_number
                    corrected_street_number = re.sub(r'(\d+)(\/|(\s\/)|(\s\/\s)|\s|\.|\,|\-)([a-zA-ZččšžĆČŠŽ]{1,2})$', r'\1\5', corrected_street_number)
                    if corrected_street_number_before != corrected_street_number:
                        corrected_street_number_errors.add('4207')
                        uncorrected_street_number_errors.remove('4207')
    
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

    customer_data = "src/processed_data/02_detected_address_errors.xlsx"

    df = pd.read_excel(customer_data)
    
    df_new = df.apply(lambda row: pd.Series(correct_names( 
        first_name=row['STREET'],
        last_name=row['HOUSE_NUMBER'],
        detected_first_name_errors=row["street_detected_errors"],
        detected_last_name_errors=row["house_number_detected_errors"],
    )), axis=1)
    
    # Convert lists to comma-separated strings just for saving
    for col in df_new.columns:
        if "errors" in col:
            df_new[col] = df_new[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)    

    # Merge original and corrected data
    final_df = pd.concat([df, df_new], axis=1)

    # Optional: Filter columns to save
    columns_to_export = [
        "CUSTOMER_ID",  #
        "STREET", 
            "corrected_street", 
            "street_detected_errors", 
            "corrected_street_errors", 
            "uncorrected_street_errors",
        "HOUSE_NUMBER", 
            "corrected_street_number", 
            "house_number_detected_errors", 
            "corrected_street_number_errors", 
            "uncorrected_street_number_errors",
        "POSTAL_CODE", 
            "corrected_zipcode", 
            "POSTAL_CODE_detected_errors", 
            "corrected_zipcode_errors", 
            "uncorrected_zipcode_errors",
        "POSTAL_CITY", 
            "corrected_city", 
            "POSTAL_CITY_detected_errors", 
            "corrected_city_errors", 
            "uncorrected_city_errors"
    ]
    
    # Save to Excel
    final_df[columns_to_export].to_excel("src/processed_data/03_corrected_address_errors.xlsx", index=False)
    
    print("✅ Correction of address errors completed and saved.")