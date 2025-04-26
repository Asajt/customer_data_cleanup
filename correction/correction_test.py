'''
import regex as re

street = ''
original_street = street
corrected_street = street

detected_street_errors = {'4105', '4103'}
corrected_street_errors = set()  
uncorrected_street_errors = detected_street_errors.copy()

if detected_street_errors:
        if '4102' in detected_street_errors: # Street error: unnecessary spaces
            corrected_street_before = corrected_street
            corrected_street = corrected_street.rstrip() # removes trailing whitespaces
            corrected_street = corrected_street.lstrip() # removes leading whitespaces
            corrected_street = re.sub(r'\s{2,}', ' ', corrected_street) # removes double whitespace
            corrected_street = re.sub(r'\s,', ',', corrected_street) # removes whitespaces before comma
            if corrected_street_before != corrected_street:
                corrected_street_errors.add('4102')
                uncorrected_street_errors.remove('4102')
                
if corrected_street != original_street:
    street = corrected_street 
else:
    street = None
    
    
print(street)
print(detected_street_errors)
print(corrected_street)
print(uncorrected_street_errors)
'''

import pandas as pd
import re

customer_data = "src/processed_data/02_detected_address_errors.xlsx"
zipcode = row['POSTAL_CODE']
detected_zipcode_errors = row["POSTAL_CODE_detected_errors"],

def split_into_set(detected_errors_column):
    if isinstance(detected_errors_column, str):
        # Split by comma, strip each item, exclude empty strings
        return set(code.strip() for code in detected_errors_column.split(",") if code.strip())
    elif isinstance(detected_errors_column, (set, list)):
        return set(str(code).strip() for code in detected_errors_column if str(code).strip())
    else:
        return set()


original_zipcode = zipcode

zipcode = "" if pd.isna(zipcode) else str(zipcode)

detected_zipcode_errors = split_into_set(detected_zipcode_errors)
corrected_zipcode_errors = set()  
uncorrected_zipcode_errors = detected_zipcode_errors.copy()

corrected_zipcode = zipcode


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

print('original zipcode:', 'I',original_zipcode,'I')
print('corrected zipcode:', 'I',corrected_zipcode,'I')
print('detected zipcode errors:', detected_zipcode_errors)
print('corrected zipcode errors:', corrected_zipcode_errors)
print('uncorrected zipcode errors:', uncorrected_zipcode_errors)