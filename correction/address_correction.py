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

def correct_address(street, street_number, zipcode, city, detected_street_errors, detected_street_number_errors, detected_zipcode_errors, detected_city_errors):
    
    hn_patterns = ['BŠ', 'B.Š.', 'B. ŠT.', 'B.ŠT.', 'B\$', 'BREZ ŠT.', 'BS', 'B.S.', 'NH', 'N.H.', 'BH', 'B.H.']
    
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

    # 3 split the string into a set
    detected_street_errors = split_into_set(detected_street_errors)
    detected_street_number_errors = split_into_set(detected_street_number_errors)
    detected_zipcode_errors = split_into_set(detected_zipcode_errors)
    detected_city_errors = split_into_set(detected_city_errors)
    
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
        if '4101' in detected_street_errors:
            corrected_street_before = corrected_street
            corrected_street = None
            if corrected_street_before != corrected_street:
                corrected_street_errors.add('4101')
                uncorrected_street_errors.remove('4101')
        
        # Street error: unnecessary spaces
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
        if '4108' in detected_street_errors:
            corrected_street_before = corrected_street
            corrected_street = re.sub(r'\.(?![\s\W])', r'. ', corrected_street)
            if corrected_street_before != corrected_street:
                corrected_street_errors.add('4108')
                uncorrected_street_errors.remove('4108')
        
        # Street error: contains variation of BŠ
        if '4106' in detected_street_errors:
            corrected_street_before = corrected_street
            for pattern in hn_patterns:
                corrected_street = re.sub(pattern, '', corrected_street, flags=re.IGNORECASE)
            if corrected_street_before != corrected_street:
                corrected_street_errors.add('4106')
                uncorrected_street_errors.remove('4106')
                    
        # Street error: invalid abbreviations
        if '4107' in detected_street_errors: 
            corrected_street_before = corrected_street
            corrected_street = corrected_street.replace('c.', 'cesta').replace('ce.', 'cesta').replace('C.', 'CESTA').replace('Ce.', 'Cesta').replace('CE.', 'CESTA')
            corrected_street = corrected_street.replace('u.','ulica').replace('ul.','ulica').replace('U.','ULICA').replace('Ul.','Ulica').replace('UL.','ULICA')
            if corrected_street_before != corrected_street:
                corrected_street_errors.add('4107')
                uncorrected_street_errors.remove('4107')
        
        #Street error: consecutive duplicates detected
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
        if '4201' in detected_street_number_errors: 
            corrected_street_number_before = corrected_street_number
            corrected_street_number = None
            if corrected_street_number_before != corrected_street_number:
                corrected_street_number_errors.add('4201')
                uncorrected_street_number_errors.remove('4201')
        
        # Street number error: unnecessary spaces
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
        if '4203' in detected_street_number_errors:
            corrected_street_number_before = corrected_street_number
            for pattern in hn_patterns:
                corrected_street_number = re.sub(pattern, '', corrected_street_number, flags=re.IGNORECASE)
            if corrected_street_number_before != corrected_street_number:
                corrected_street_number_errors.add('4203')
                uncorrected_street_number_errors.remove('4203')
                
        # remove leading 0s
        if '4206' in detected_street_number_errors: 
            corrected_street_number_before = corrected_street_number
            corrected_street_number = corrected_street_number.lstrip('0')
            if corrected_street_number_before != corrected_street_number:
                corrected_street_number_errors.add('4206')
                uncorrected_street_number_errors.remove('4206')
        
        # remove dots
        if '4209' in detected_street_number_errors:
            corrected_street_number_before = corrected_street_number
            corrected_street_number = corrected_street_number.rstrip('.')
            if corrected_street_number_before != corrected_street_number:
                corrected_street_number_errors.add('4209')
                uncorrected_street_number_errors.remove('4209')
        
        # correct spacing in between house number components
        if '4205' in detected_street_number_errors and not (
                '4208' in detected_street_number_errors or #roman numerals
                '4209' in detected_street_number_errors): #ends with a full stop
            corrected_street_number_before = corrected_street_number
            corrected_street_number = re.sub(r'(\d+)(\/|(\s\/)|(\s\/\s)|\s|\.|\,|\-)([a-zA-ZččšžĆČŠŽ]{1,2})$', r'\1\5', corrected_street_number)
            if corrected_street_number_before != corrected_street_number:
                corrected_street_number_errors.add('4205')
                uncorrected_street_number_errors.remove('4205')
        
        # street number error: invalid spacing between house number components    
        if '4207' in detected_street_number_errors and not (
                '4208' in detected_street_number_errors): #roman numerals
            corrected_street_number_before = corrected_street_number
            corrected_street_number = re.sub(r'(\d+)(\/|(\s\/)|(\s\/\s)|\s|\.|\,|\-)([a-zA-ZččšžĆČŠŽ]{1,2})$', r'\1\5', corrected_street_number)
            if corrected_street_number_before != corrected_street_number:
                corrected_street_number_errors.add('4207')
                uncorrected_street_number_errors.remove('4207')
            
    # Zipcode corrections 
    if detected_zipcode_errors:
        # missing data 
        if '4301' in detected_zipcode_errors: 
            corrected_zipcode_before = corrected_zipcode
            corrected_zipcode = None
            if corrected_zipcode_before != corrected_zipcode:
                corrected_zipcode_errors.add('4301')
                uncorrected_zipcode_errors.remove('4301')
    
        # Zipcode error: unnecessary spaces
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
        if '4401' in detected_city_errors: 
            corrected_city_before = corrected_city
            corrected_city = None
            if corrected_city_before != corrected_city:
                corrected_city_errors.add('4401')
                uncorrected_city_errors.remove('4401')
        
        # City error: unnecessary spaces
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

    return {
    "corrected_street": corrected_street if corrected_street != original_street else None,
    "corrected_street_errors": sorted(corrected_street_errors),
    "uncorrected_street_errors": sorted(uncorrected_street_errors),

    "corrected_street_number": corrected_street_number if corrected_street_number != original_street_number else None,
    "corrected_street_number_errors": sorted(corrected_street_number_errors),
    "uncorrected_street_number_errors": sorted(uncorrected_street_number_errors),

    "corrected_zipcode": corrected_zipcode if corrected_zipcode != original_zipcode else None,
    "corrected_zipcode_errors": sorted(corrected_zipcode_errors),
    "uncorrected_zipcode_errors": sorted(uncorrected_zipcode_errors),

    "corrected_city": corrected_city if corrected_city != original_city else None,
    "corrected_city_errors": sorted(corrected_city_errors),
    "uncorrected_city_errors": sorted(uncorrected_city_errors)
    }

    

if __name__ == "__main__":

    # TESTING

    customer_data = "src/processed_data/02_detected_address_errors.xlsx"

    df = pd.read_excel(customer_data)
    
    df_new = df.apply(lambda row: pd.Series(correct_address( 
        street=row['STREET'],
        street_number=row['HOUSE_NUMBER'],
        zipcode=row['POSTAL_CODE'],
        city=row['POSTAL_CITY'],
        detected_street_errors=row["street_detected_errors"],
        detected_street_number_errors=row["house_number_detected_errors"],
        detected_zipcode_errors=row["POSTAL_CODE_detected_errors"],
        detected_city_errors=row["POSTAL_CITY_detected_errors"]
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
