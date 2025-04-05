import pandas as pd
import re

def correct_address(street, street_number, zipcode, city, detected_errors):
    
    # Store the original address components for comparison purposes
    original_street = street
    original_street_number = street_number
    original_zipcode = zipcode
    original_city = city

    # Check for NaN values and convert them to empty strings
    street = "" if pd.isna(street) else str(street)
    street_number = "" if pd.isna(street_number) else str(street_number)
    zipcode = "" if pd.isna(zipcode) else str(zipcode)
    city = "" if pd.isna(city) else str(city)

    if isinstance(detected_errors, str):
        detected_errors = set(detected_errors.split(",")) if detected_errors else set()
    else:
        detected_errors = set()
        
    orig_detected_errors = detected_errors.copy() # Store the original detected errors for comparison
    corrected_errors = set()  # Set to store errors corrected during processing
    uncorrected_errors = set()  # Set to store errors that remain uncorrected

    error_messages = {
        '101': 'Street error: no information given',
        '102': 'Street error: unnecessary spaces',
        '103': 'Street error: contains \'BŠ\' or \'NH\'',
        '104': 'Street error: contains house number',
        '105': 'Street error: invalid characters',
        '106': 'Street error: invalid abbreviations',
        '107': 'Street error: no space after full stop',
        '108': 'Street error: only numbers',
        '109': 'Street error: consecutive duplicates detected',
        '110': 'Street error: street name beginning with a digit',
        '111': 'Street error: invalid digit in Street',

        '201': 'Street number error: no information given',
        '202': 'Street number error: unnecessary spaces',
        '203': 'Street number error: contains \'BŠ\' or \'NH\'',
        '204': 'Street number error: no house number',
        '205': 'Street number error: invalid combination',
        '206': 'Street number error: house number with leading 0',
        '207': 'Street number error: spacing between house number components',

        '301': 'Zipcode error: no information given',
        '302': 'Zipcode error: unnecessary spaces',
        '303': 'Zipcode error: invalid characters',
        '304': 'Zipcode error: more than 4 digits',
        '305': 'Zipcode error: less than 4 digits',

        '401': 'City error: no information given',
        '402': 'City error: unnecessary spaces',
        '403': 'City error: contains digits',
        '404': 'City error: invalid characters',
        '405': 'City error: invalid abbreviations',
        '406': 'City error: no space after full stop',
        '407': 'City error: consecutive duplicates detected'
    }
    
    '''
    error_messages2 = {
        '4101': 'STREET_NAME: Missing Data',
        '4102': 'STREET_NAME: Unnecessary Spaces',
        '4103': 'STREET_NAME: Invalid characters',
        '4104': 'STREET_NAME: Contains house number',
        '4105': 'STREET_NAME: Contains variation of BŠ',
        '4106': 'STREET_NAME: Invalid abbreviations',
        '4107': 'STREET_NAME: No space after full stop',
        '4108': 'STREET_NAME: Only numbers',
        '4109': 'STREET_NAME: Duplicates',
        '4110': 'STREET_NAME: Starts with number',
        '4111': 'STREET_NAME: More than 2 commas',
        '4112': 'STREET_NAME: Cannot contain digit at the end',
        
        '4201': 'HOUSE_NUMBER: Missing Data',
        '4202': 'HOUSE_NUMBER: Unnecessary spaces',
        '4203': 'HOUSE_NUMBER: Contains variation of BŠ',
        '4203': 'HOUSE_NUMBER: Contains variation of BŠ',
        '4204': 'HOUSE_NUMBER: No house number',
        '4205': 'HOUSE_NUMBER: invalid combination',
        '4206': 'HOUSE_NUMBER: Leading 0',
        '4207': 'HOUSE_NUMBER: Spacing between components',
        '4208': 'HOUSE_NUMBER: Contains roman numerals',
        
        '4301': 'ZIPCODE: Missing Data',
        '4302': 'ZIPCODE: Unnecessary Spaces',
        '4303': 'ZIPCODE: invalid characters',
        '4304': 'ZIPCODE: Less than 4',
        '4305': 'ZIPCODE: More than 4',
        '4306': 'ZIPCODE: Contains Letters',
        '4307': 'ZIPCODE: Invalid Value',
        
        '4401': 'POSTAL_CITY: Missing Data',
        '4402': 'POSTAL_CITY: Unnecessary Spaces',
        '4403': 'POSTAL_CITY: Invalid characters',
        '4404': 'POSTAL_CITY: Contains digits',
        '4405': 'POSTAL_CITY: Invalid abbreviations',
        '4406': 'POSTAL_CITY: Duplicates'
    }
    '''
    
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

    # Loop to decide how many times to process the address
    n = 3
    for i in range(n):

        corrected_street = street
        corrected_street_number = street_number
        corrected_zipcode = zipcode
        corrected_city = city

        # Street corrections 
        if detected_errors:
            if '102' in detected_errors: # Street error: unnecessary spaces
                corrected_street_before = corrected_street
                corrected_street = corrected_street.rstrip() # removes trailing whitespaces
                corrected_street = corrected_street.lstrip() # removes leading whitespaces
                corrected_street = re.sub(r'\s{2,}', ' ', corrected_street) # removes double whitespace
                corrected_street = re.sub(r'\s,', ',', corrected_street) # removes whitespaces before comma
                if corrected_street_before != corrected_street:
                    corrected_errors.add('102')
                    detected_errors.remove('102')
            if '107' in detected_errors: # Street error: no space after full stop
                corrected_street_before = corrected_street
                corrected_street = re.sub(r'\.(?![\s\W])', r'. ', corrected_street)
                if corrected_street_before != corrected_street:
                    corrected_errors.add('107')
                    detected_errors.remove('107')
            if '106' in detected_errors: # Street error: invalid abbreviations
                corrected_street_before = corrected_street
                corrected_street = corrected_street.replace('c.', 'cesta').replace('u.','ulica').replace('ul.','ulica').replace('C.', 'CESTA').replace('U.','ULICA').replace('UL.','ULICA').replace('Ul.','Ulica')
                if corrected_street_before != corrected_street:
                    corrected_errors.add('106')
                    detected_errors.remove('106')
            if '109' in detected_errors: #Street error: consecutive duplicates detected
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
                    corrected_errors.add('109')
                    detected_errors.remove('109')

        # Street number corrections 
        if detected_errors:
            if '202' in detected_errors: # Street number error: unnecessary spaces
                corrected_street_number_before = corrected_street_number
                corrected_street_number = corrected_street_number.rstrip() # removes trailing whitespaces
                corrected_street_number = corrected_street_number.lstrip() # removes leading whitespaces
                corrected_street_number = re.sub(r'\s{2,}', ' ', corrected_street_number) # removes double whitespace
                corrected_street_number = re.sub(r'\s,', ',', corrected_street_number) # removes whitespaces before comma
                if corrected_street_number_before != corrected_street_number:
                    corrected_errors.add('202')
                    detected_errors.remove('202')
            if '206' in detected_errors:
                corrected_street_number_before = corrected_street_number
                corrected_street_number = re.sub(r'\b0+\s*(\d+)', r'\1', corrected_street_number)
                if corrected_street_number_before != corrected_street_number:
                    corrected_errors.add('206')
                    detected_errors.remove('206')
            if '205' in detected_errors:
                corrected_street_number_before = corrected_street_number
                corrected_street_number = corrected_street_number.rstrip('.')
                if corrected_street_number_before != corrected_street_number:
                    corrected_errors.add('205')
                    detected_errors.remove('205')
            if '207' in detected_errors and not ('209' in detected_errors or '208' in detected_errors):
                corrected_street_number_before = corrected_street_number
                corrected_street_number = re.sub(r'(\d+)(\/|(\s\/)|(\s\/\s)|\s|\.|\,|\-)([a-zA-ZččšžĆČŠŽ]{1,2})$', r'\1\5', corrected_street_number)
                if corrected_street_number_before != corrected_street_number:
                    corrected_errors.add('207')
                    detected_errors.remove('207')

        # Zipcode corrections 
        if detected_errors:
            if '302' in detected_errors: # Zipcode error: unnecessary spaces
                corrected_zipcode_before = corrected_zipcode
                corrected_zipcode = corrected_zipcode.rstrip() # removes trailing whitespaces
                corrected_zipcode = corrected_zipcode.lstrip() # removes leading whitespaces
                corrected_zipcode = re.sub(r'\s{2,}', ' ', corrected_zipcode) # removes double whitespace
                corrected_zipcode = re.sub(r'\s,', ',', corrected_zipcode) # removes whitespaces before comma
                if corrected_zipcode_before != corrected_zipcode:
                    corrected_errors.add('302')
                    detected_errors.remove('302')

        # City corrections 
        if detected_errors:
            if '402' in detected_errors: # City error: unnecessary spaces
                corrected_city_before = corrected_city
                corrected_city = corrected_city.rstrip() # removes trailing whitespaces
                corrected_city = corrected_city.lstrip() # removes leading whitespaces
                corrected_city = re.sub(r'\s{2,}', ' ', corrected_city) # removes double whitespace
                corrected_city = re.sub(r'\s,', ',', corrected_city) # removes whitespaces before comma
                if corrected_city_before != corrected_city:
                    corrected_errors.add('402')
                    detected_errors.remove('402')
            if '406' in detected_errors: #Street error: consecutive duplicates detected
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
                    corrected_errors.add('406')
                    detected_errors.remove('406')

        # Update address components for next iteration
        street = corrected_street
        street_number = corrected_street_number
        zipcode = corrected_zipcode
        city = corrected_city

    # After all iterations, determine uncorrected errors
    uncorrected_errors = detected_errors.difference(orig_detected_errors)
        
    # Compare the input with the corrected address parts, if there is a difference update the corrected column, if not, keep it blank 
    if corrected_street != original_street:
        street = corrected_street 
    else:
        street = None
        
    if corrected_street_number != original_street_number:
        street_number = corrected_street_number
    else:
        street_number = None
        
    if corrected_zipcode != original_zipcode:
        zipcode = corrected_zipcode
    else:
        zipcode = None
        
    if corrected_city != original_city:
        city = corrected_city
    else:
        city = None

    return (
        street, 
        street_number, 
        zipcode, 
        city, 
        ','.join(sorted(orig_detected_errors)), 
        ','.join(sorted(uncorrected_errors))
    )

# TESTING

customer_data = "src/processed_data/customer_data_with_detected_errors.xlsx"

df = pd.read_excel(customer_data)

df_new = df.apply(lambda row: pd.Series(correct_address(row['STREET'], row['HOUSE_NUMBER'], row['POSTAL_CODE'], row['POSTAL_CITY'], row['DETECTED_ERRORS'])), axis=1)

# set column names for `df_new`
df_new.columns = [
    "CORRECTED_STREET", "CORRECTED_HOUSE_NUMBER", "CORRECTED_POSTAL_CODE", "CORRECTED_CITY", 
    "DETECTED_ERRORS", "UNCORRECTED_ERRORS"
]

address_df = pd.DataFrame({
    "ORIG_STREET": df["STREET"],
    "CORRECTED_STREET": df_new["CORRECTED_STREET"],

    "ORIG_HOUSE_NUMBER": df["HOUSE_NUMBER"],
    "CORRECTED_HOUSE_NUMBER": df_new["CORRECTED_HOUSE_NUMBER"],

    "ORIG_POSTAL_CODE": df["POSTAL_CODE"],
    "CORRECTED_POSTAL_CODE": df_new["CORRECTED_POSTAL_CODE"],

    "ORIG_POSTAL_CITY": df["POSTAL_CITY"],
    "CORRECTED_POSTAL_CITY": df_new["CORRECTED_CITY"],

    "INTRODUCED_ERRORS": df["introduced_errors"],
    "DETECTED_ERRORS": df_new["DETECTED_ERRORS"],
    "UNCORRECTED_ERRORS": df_new["UNCORRECTED_ERRORS"]
})

# print(address_df.head())
address_df.to_excel("src/processed_data/02_customer_data_with_corrected_address.xlsx", index=False)
print("Correction of address errors completed!")