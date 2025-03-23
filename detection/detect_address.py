
import pandas as pd
import re

def detect_address_errors(street, street_number, zipcode, city):

    # Check for NaN values and convert them to empty strings
    street = "" if pd.isna(street) else str(street)
    street_number = "" if pd.isna(street_number) else str(street_number)
    zipcode = "" if pd.isna(zipcode) else str(zipcode)
    city = "" if pd.isna(city) else str(city)

    errors = set()
    
    error_messages = {
        '4101': 'STREET_NAME: Missing Data',
        '4102': 'STREET_NAME: Unnecessary Spaces',
        '4103': 'STREET_NAME: Invalid characters',
        '4104': 'STREET_NAME: Formatting Issue',
        '4105': 'STREET_NAME: Contains house number',
        '4106': 'STREET_NAME: Contains variation of BŠ',
        '4107': 'STREET_NAME: Invalid abbreviations',
        '4108': 'STREET_NAME: No space after full stop',
        '4109': 'STREET_NAME: Only numbers',
        '4110': 'STREET_NAME: Duplicates',
        '4111': 'STREET_NAME: Starts with number',
        '4112': 'STREET_NAME: Cannot contain digit at the end',
        '4113': 'STREET_NAME: Invalid digit in Street',
        '4114': 'STREET_NAME: replacing šćčž to scz',
        
        '4201': 'HOUSE_NUMBER: Missing Data',
        '4202': 'HOUSE_NUMBER: Unnecessary spaces',
        '4203': 'HOUSE_NUMBER: Contains variation of BŠ',
        '4204': 'HOUSE_NUMBER: No house number',
        '4205': 'HOUSE_NUMBER: invalid combination',
        '4206': 'HOUSE_NUMBER: Leading 0',
        '4207': 'HOUSE_NUMBER: Spacing between components',
        '4208': 'HOUSE_NUMBER: Contains roman numerals',
        '4209': 'HOUSE_NUMBER: Ends with full stop',
        '4210': 'HOUSE_NUMBER: More than one number present',
        '4211': 'HOUSE_NUMBER: Does not start with digit',
        '4212': 'HOUSE_NUMBER: More than 4 digits',
        
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
        '4404': 'POSTAL_CITY: Formatting Issue',
        '4405': 'POSTAL_CITY: Contains digits',
        '4406': 'POSTAL_CITY: Invalid abbreviations',
        '4407': 'POSTAL_CITY: Duplicates',
        '4408': 'POSTAL_CITY: replacing šćčž to scz'
    }
    
    
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

    # Street errors
    if pd.isna(street) or street is None or street.strip() == "" or street.strip() == "/" :
        errors.add('4101')  # Missing Data OK
    else:
        if re.search(r'^\d',street):
            errors.add('4111')  # Starts with number OK
        if street.startswith(' ') or street.endswith(' ') or "  " in street:
            errors.add('4102')  # Unnecessary Spaces OK
        if any(re.search(r'\b' + re.escape(pattern) + r'\b', street) for pattern in hn_patterns):
            errors.add('4106')  # Contains variation of BŠ OK
        if not re.search(r'^[a-zA-ZčćšžČĆŠŽ\d\s\.,-/]+$', street) or '//' in street:
            errors.add('4103')  # Invalid characters OK
        # !!!  Formatting issues (check whether the case of letters is correct) 
        if re.search(r'(?<!\d)\.',street) and re.search(r'\b(?!(?:' + '|'.join(allowed_abbreviations_street) + r')\.)\w+\.', street, flags=re.IGNORECASE): 
            errors.add('4107')  # Invalid abbreviations OK
        if not any(char.isalpha() for char in street):
            errors.add('4109')  # Only numbers OK
        if street:
            components = [comp.replace(',', '').upper() 
                        for comp in re.split(r'\s+', street) if comp]
            prev_comp = None
            for comp in components:
                if prev_comp and prev_comp == comp:
                    errors.add('4110')    # (consecutive) Duplicates OK
                    break 
                prev_comp = comp
        if re.search(r'\d+[A-Za-zČčŠšŽž]{0,3}(\/?|\.?|\s?)[A-Za-zČčŠšŽž]{0,3}$', street):
            errors.add('4105') # Contains house number OK
        # !!! cannot contain digit at the end
        if not '4105' in errors and re.search(r'\d+$', street):
            errors.add('4112')
        if not '4105' in errors and not '4107' in errors and street and re.search(r'\.(?![\s\W])',street):
            errors.add('4108')  # No space after full stop OK
        if not '4105' in errors and re.search(r'\d+(?![.\d])', street) and not re.search(r'25\s+TALCEV',street): #edina ulica, ki nima pike po številki 2024/03/12
                errors.add('4113')  #Street error: invalid digit in Street OK
        # !!! replacing šćčž to scz

    # Street_number errors 
    if pd.isna(street_number) or street_number is None or street_number.strip() == "" or street_number.strip() == ".":
        errors.add('4201')  # Missing data 
    else:
        if re.search(r'\b(?:' + '|'.join(roman_numbers) + r')\d*\b', street_number, flags=re.IGNORECASE):
            errors.add('4208')  # Contains roman numerals
        if street_number.startswith(' ') or street_number.endswith(' ') or "  " in street_number:
            errors.add('4202')  # Unnecessary spaces
        if any(pattern in street_number for pattern in hn_patterns) and re.search(r'\d', street_number):
            errors.add('213') # Street number error: contains BŠ as well as a number
        if not '213' in errors and any(pattern in street_number for pattern in hn_patterns):
            errors.add('4203')  # Contains variation of BŠ
        if not '4203' in errors  and street_number.endswith('.') and re.search(r'\d', street_number):
            errors.add('205') # Street number error: ends with full stop
        if len(re.findall(r'\d+', street_number)) > 1:
            errors.add('210')  # Street number error: more than one number present
        if not ('4202' in errors or '4203' in errors or '4208' in errors or '208' in errors) and not re.search(r'\d', street_number) or re.search(r'^[^1-9]*0[^1-9]*$', street_number):
            errors.add('4204')  # No house number
        if not ('4202' in errors or '4203' in errors or '4208' in errors or '4204' in errors) and re.search(r'^[^0-9]',street_number):
            errors.add('208')  # Street number error: does not start with digit
        if not '4204' in errors and re.findall(r'\d{4,}', street_number):
            errors.add('211')  #Street number error: 4 digits
        if not ('4203' in errors or '210' in errors or '4208' in errors or '208' in errors or '211' in errors) and re.search(r'(\d+)(\/|(\s\/)|(\s\/\s)|\s|\.|\,|\-)([a-zA-ZččšžĆČŠŽ]{1,2})$', street_number):
            errors.add('4207')  # Spacing / invalid characters between components 
        if not '4204' in errors and re.search(r'\b0\s*\d+', street_number): 
            errors.add('4206')  # Leading 0
        if not errors and not re.search(r'^\d{1,3}[A-Za-zČčŠšŽž]{0,2}$', street_number):
            errors.add('4205')  # Invalid combination

    # Zipcode errors        
    if pd.isna(zipcode) or zipcode is None or zipcode.strip() == "":
        errors.add('4301')  # Missing data
    else:
        if len(re.findall(r'\d', zipcode)) > 4:
            errors.add('4305')  # More than 4 digits
        if len(re.findall(r'\d', zipcode)) < 4:
            errors.add('4304')  # Less than 4 digits
        if zipcode.startswith(' ') or zipcode.endswith(' ') or "  " in zipcode:
            errors.add('4302')  # Unnecessary spaces
        if not '4302' in errors and not re.search(r'^\d+$',zipcode):
            errors.add('4303')  # Invalid characters
        elif not (999 < int(zipcode) <= 9265) and '4305' not in errors and '4304' not in errors:
            errors.add('4307')  # Invalid Value

    # City errors
    if pd.isna(city) or city is None or city.strip() == "" or city.strip() == "/" :
        errors.add('4401')  # Missing data
    else:
        if city.startswith(' ') or city.endswith(' ') or "  " in city:
            errors.add('4402')  # Unnecessary spaces
        if re.search(r'[^a-zA-ZčČšŠžŽ\s]', city):
            errors.add('4403')  # Invalid characters
        if re.search(r'\d', city):
            errors.add('4405') # Contains digits
        if re.search(r'\b(?!(?:' + '|'.join(allowed_abbreviations_city) + r')\.)\w+\.', city, flags=re.IGNORECASE): 
            errors.add('4406')  # Invalid abbreviations
        if city:
            components = [comp.replace(',', '').upper() 
                        for comp in re.split(r'\s+', city) if comp]
            prev_comp = None
            for comp in components:
                if prev_comp and prev_comp == comp:
                    errors.add('4407')    # (consecutive) Duplicates
                    break 
                prev_comp = comp

    return ','.join(sorted(errors))

# # ============================
# # **EXECUTION**
# # ============================

customer_data = "src/processed_data/customer_data_with_errors.xlsx"
df = pd.read_excel(customer_data)

df["DETECTED_ERRORS"] = df.apply(lambda row: detect_address_errors(
    row["STREET"], row["HOUSE_NUMBER"], row["POSTAL_CODE"], row["POSTAL_CITY"]), axis=1)

df.to_excel("src/processed_data/01_customer_data_with_detected_errors.xlsx", index=False)
print("Detection of address errors completed!")