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

def correct_address(street, street_number, zipcode, city, detected_street_errors, detected_street_number_errors, detected_zipcode_errors, detected_city_errors):
    """
    Corrects address components based on detected errors.

    This function takes individual address components (street, street number, postal code, and city) 
    along with their respective detected error sets and applies corrections based on predefined rules 
    and configurations. It returns the corrected address components along with updated error sets.

    Args:
        street (str): The street name of the address.
        street_number (str): The house number of the address.
        zipcode (str): The postal code of the address.
        city (str): The city name of the address.
        detected_street_errors (set): A set of detected error codes for the street.
        detected_street_number_errors (set): A set of detected error codes for the house number.
        detected_zipcode_errors (set): A set of detected error codes for the postal code.
        detected_city_errors (set): A set of detected error codes for the city.

    Returns:
        dict: A dictionary containing the following keys:
            - corrected_street (str or None): The corrected street name, or None if no correction was made.
            - corrected_street_errors (list): A sorted list of corrected error codes for the street.
            - uncorrected_street_errors (list): A sorted list of uncorrected error codes for the street.
            - corrected_street_number (str or None): The corrected house number, or None if no correction was made.
            - corrected_street_number_errors (list): A sorted list of corrected error codes for the house number.
            - uncorrected_street_number_errors (list): A sorted list of uncorrected error codes for the house number.
            - corrected_zipcode (str or None): The corrected postal code, or None if no correction was made.
            - corrected_zipcode_errors (list): A sorted list of corrected error codes for the postal code.
            - uncorrected_zipcode_errors (list): A sorted list of uncorrected error codes for the postal code.
            - corrected_city (str or None): The corrected city name, or None if no correction was made.
            - corrected_city_errors (list): A sorted list of corrected error codes for the city.
            - uncorrected_city_errors (list): A sorted list of uncorrected error codes for the city.
    """
    
    # 01. Store the original address components for comparison purposes
    original_street = street
    original_street_number = street_number
    original_zipcode = zipcode
    original_city = city

    # 02. Check for NaN values and convert them to empty strings
    street = "" if pd.isna(street) else str(street)
    street_number = "" if pd.isna(street_number) else str(street_number)
    zipcode = "" if pd.isna(zipcode) else str(zipcode)
    city = "" if pd.isna(city) else str(city)
    
    corrected_street_errors = set()  
    uncorrected_street_errors = detected_street_errors.copy()
    
    corrected_street_number_errors = set()  
    uncorrected_street_number_errors = detected_street_number_errors.copy()
    
    corrected_zipcode_errors = set()  
    uncorrected_zipcode_errors = detected_zipcode_errors.copy()
    
    corrected_city_errors = set()  
    uncorrected_city_errors = detected_city_errors.copy()
    
    # values to compare with in checks and corrections
    roman_numbers = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'
                    , 'XI', 'XII', 'XIII', 'XIV','XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX'
                    , 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII', 'XXVIII', 'XXIX', 'XXX'
                    , 'XXXI'
                    , 'XL']
    allowed_abbreviations_street = ['dr', 'Sv', 'Vel']
    allowed_abbreviations_street.extend(roman_numbers)

    allowed_abbreviations_city = ['Sv', 'Slov']
    
    hn_patterns = ['BŠ', 'B.Š.', 'B. ŠT.', 'B.ŠT.', 'B$', 'BREZ ŠT.', 'BS', 'B.S.', 'NH', 'N.H.', 'BH', 'B.H.']

    corrected_street = street
    corrected_street_number = street_number
    corrected_zipcode = zipcode
    corrected_city = city

    # Street corrections 
    if detected_street_errors:
        # missing data 
        if should_correct('4101', error_config):
            if '4101' in detected_street_errors:
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
    if detected_street_number_errors:
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
                    
    # Zipcode corrections 
    if detected_zipcode_errors:
        # missing data 
        if should_correct('4301', error_config):
            if '4301' in detected_zipcode_errors: 
                corrected_zipcode_before = corrected_zipcode
                corrected_zipcode = None
                if corrected_zipcode_before != corrected_zipcode:
                    corrected_zipcode_errors.add('4301')
                    uncorrected_zipcode_errors.remove('4301')
        
        # Zipcode error: unnecessary spaces
        if should_correct('4302', error_config):
            if '4302' in detected_zipcode_errors: 
                corrected_zipcode_before = corrected_zipcode
                corrected_zipcode = corrected_zipcode.rstrip() # removes trailing whitespaces
                corrected_zipcode = corrected_zipcode.lstrip() # removes leading whitespaces
                corrected_zipcode = re.sub(r'\s{2,}', ' ', corrected_zipcode) # removes double whitespace
                corrected_zipcode = re.sub(r'\s,', ',', corrected_zipcode) # removes whitespaces before comma
                if corrected_zipcode_before != corrected_zipcode:
                    corrected_zipcode_errors.add('4302')
                    uncorrected_zipcode_errors.remove('4302')

    # City corrections 
    if detected_city_errors:
        # missing data 
        if should_correct('4401', error_config):
            if '4401' in detected_city_errors: 
                corrected_city_before = corrected_city
                corrected_city = None
                if corrected_city_before != corrected_city:
                    corrected_city_errors.add('4401')
                    uncorrected_city_errors.remove('4401')
            
        # City error: unnecessary spaces
        if should_correct('4402', error_config):
            if '4402' in detected_city_errors: 
                corrected_city_before = corrected_city
                corrected_city = corrected_city.rstrip() # removes trailing whitespaces
                corrected_city = corrected_city.lstrip() # removes leading whitespaces
                corrected_city = re.sub(r'\s{2,}', ' ', corrected_city) # removes double whitespace
                corrected_city = re.sub(r'\s,', ',', corrected_city) # removes whitespaces before comma
                if corrected_city_before != corrected_city:
                    corrected_city_errors.add('4402')
                    uncorrected_city_errors.remove('4402')
        
        #Street error: consecutive duplicates detected
        if should_correct('4407', error_config):
            if '4407' in detected_city_errors: 
                corrected_city_before = corrected_city
                # Split the string into parts
                city_parts = city.replace(',', '').split()
                # List to keep track of items already added (in lowercase for comparison)
                seen = set()
                # List for the result, preserving original case
                city_unique_parts = []
                for part in city_parts:
                    # Convert part to lowercase for case-insensitive comparison
                    if part.upper() not in seen:
                        seen.add(part.upper())  # Add lowercase version to seen for comparison
                        city_unique_parts.append(part)  # Add original part to result
                # Join the unique parts back together
                corrected_city = ' '.join(city_unique_parts)
                if corrected_city_before != corrected_city:
                    corrected_city_errors.add('4407')
                    uncorrected_city_errors.remove('4407')

    return (
    corrected_street if corrected_street != original_street else None,
    sorted(corrected_street_errors),
    sorted(uncorrected_street_errors),

    corrected_street_number if corrected_street_number != original_street_number else None,
    sorted(corrected_street_number_errors),
    sorted(uncorrected_street_number_errors),

    corrected_zipcode if corrected_zipcode != original_zipcode else None,
    sorted(corrected_zipcode_errors),
    sorted(uncorrected_zipcode_errors),

    corrected_city if corrected_city != original_city else None,
    sorted(corrected_city_errors),
    sorted(uncorrected_city_errors)
    )    

if __name__ == "__main__":

    customer_data = "src/processed_data/02_detected_address_errors.xlsx"

    df = pd.read_excel(customer_data)
    
    # split the string into a set
    df['street_detected_errors'] = df['street_detected_errors'].apply(split_into_set)
    df['house_number_detected_errors'] = df['house_number_detected_errors'].apply(split_into_set)
    df['POSTAL_CODE_detected_errors'] = df['POSTAL_CODE_detected_errors'].apply(split_into_set)
    df['POSTAL_CITY_detected_errors'] = df['POSTAL_CITY_detected_errors'].apply(split_into_set)
    
    # Apply the correction function to each row
    df[["corrected_street", "corrected_street_errors", "uncorrected_street_errors",
        "corrected_street_number", "corrected_street_number_errors", "uncorrected_street_number_errors",
        "corrected_zipcode", "corrected_zipcode_errors", "uncorrected_zipcode_errors",
        "corrected_city", "corrected_city_errors", "uncorrected_city_errors"]] = df.apply(
        lambda row: pd.Series(correct_address(
            street=row['STREET'],
            street_number=row['HOUSE_NUMBER'],
            zipcode=row['POSTAL_CODE'],
            city=row['POSTAL_CITY'],
            detected_street_errors=row["street_detected_errors"],
            detected_street_number_errors=row["house_number_detected_errors"],
            detected_zipcode_errors=row["POSTAL_CODE_detected_errors"],
            detected_city_errors=row["POSTAL_CITY_detected_errors"]
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
    # df[columns_to_export].to_excel("src/processed_data/03_corrected_address_errors.xlsx", index=False)
    print(df[columns_to_export].head(10))
    print("✅ Correction of address errors completed and saved.")