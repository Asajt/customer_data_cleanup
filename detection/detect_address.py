
import pandas as pd
import re

def detect_address(street, street_number, zipcode, city):

    # Check for NaN values and convert them to empty strings
    street = "" if pd.isna(street) else str(street)
    street_number = "" if pd.isna(street_number) else str(street_number)
    zipcode = "" if pd.isna(zipcode) else str(zipcode)
    city = "" if pd.isna(city) else str(city)

    errors = set()

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

    # Street errors
    if pd.isna(street) or street is None or street.strip() == "" or street.strip() == "/" :
        errors.add('101')  # Street error: no information given
    else:
        if re.search(r'^\d',street):
            errors.add('110')  #Street error: street name beginning with a digit
        if street.startswith(' ') or street.endswith(' ') or "  " in street:
            errors.add('102')  #Street error: unnecessary spaces
        if any(re.search(r'\b' + re.escape(pattern) + r'\b', street) for pattern in hn_patterns):
            errors.add('103')  #Street error: contains 'BŠ' or 'NH' 
        if not re.search(r'^[a-zA-ZčćšžČĆŠŽ\d\s\.,-/]+$', street) or '//' in street:
            errors.add('105')  #Street error: invalid characters
        if re.search(r'(?<!\d)\.',street) and re.search(r'\b(?!(?:' + '|'.join(allowed_abbreviations_street) + r')\.)\w+\.', street, flags=re.IGNORECASE): 
            errors.add('106')  #Street error: invalid abbreviations

        if not any(char.isalpha() for char in street):
            errors.add('108')  #Street error: only numbers
        if street:
            components = [comp.replace(',', '').upper() 
                        for comp in re.split(r'\s+', street) if comp]
            prev_comp = None
            for comp in components:
                if prev_comp and prev_comp == comp:
                    errors.add('109')    # Street error: consecutive duplicates detected
                    break 
                prev_comp = comp
        if re.search(r'\d+[A-Za-zČčŠšŽž]{0,3}(\/?|\.?|\s?)[A-Za-zČčŠšŽž]{0,3}$', street):
            errors.add('104') # Street error: contains house number
        if not '104' in errors and street and re.search(r'\.(?![\s\W])',street):
            errors.add('107')  #Street error: no space after full stop
        if not '104' in errors and re.search(r'\d+(?![.\d])', street) and not re.search(r'25\s+TALCEV',street): #edina ulica, ki nima pike po številki 2024/03/12
                errors.add('111')  #Street error: invalid digit in Street

    # Street_number errors 
    if pd.isna(street_number) or street_number is None or street_number.strip() == "" or street_number.strip() == ".":
        errors.add('201')  # Street number error: no information given
    else:
        if re.search(r'\b(?:' + '|'.join(roman_numbers) + r')\d*\b', street_number, flags=re.IGNORECASE):
            errors.add('209')  # Street number error: contains roman numerals
        if street_number.startswith(' ') or street_number.endswith(' ') or "  " in street_number:
            errors.add('202')  # Street number error: unnecessary spaces
        if any(pattern in street_number for pattern in hn_patterns) and re.search(r'\d', street_number):
            errors.add('213') # Street number error: contains BŠ as well as a number
        if not '213' in errors and any(pattern in street_number for pattern in hn_patterns):
            errors.add('203')  # Street number error: contains 'BŠ' or 'NH' 
            errors.add('203')
        if not '203' in errors  and street_number.endswith('.') and re.search(r'\d', street_number):
            errors.add('205') # Street number error: ends with full stop
        if len(re.findall(r'\d+', street_number)) > 1:
            errors.add('210')  # Street number error: more than one number present
        if not ('202' in errors or '203' in errors or '209' in errors or '208' in errors) and not re.search(r'\d', street_number) or re.search(r'^[^1-9]*0[^1-9]*$', street_number):
            errors.add('204')  # Street number error: no house number
        if not ('202' in errors or '203' in errors or '209' in errors or '204' in errors) and re.search(r'^[^0-9]',street_number):
            errors.add('208')  # Street number error: does not start with digit
        if not '204' in errors and re.findall(r'\d{4,}', street_number):
            errors.add('211')  #Street number error: 4 digits
        if not ('203' in errors or '210' in errors or '209' in errors or '208' in errors or '211' in errors) and re.search(r'(\d+)(\/|(\s\/)|(\s\/\s)|\s|\.|\,|\-)([a-zA-ZččšžĆČŠŽ]{1,2})$', street_number):
            errors.add('207')  # Street number error: invalid characters between house number components
        if not '204' in errors and re.search(r'\b0\s*\d+', street_number): 
            errors.add('206')  # Street number error: house number with leading 0
        if not errors and not re.search(r'^\d{1,3}[A-Za-zČčŠšŽž]{0,2}$', street_number):
            errors.add('212')  # Street number error: invalid combination

    # Zipcode errors        
    if pd.isna(zipcode) or zipcode is None or zipcode.strip() == "":
        errors.add('301')  # Zipcode error: no information given
    else:
        if len(re.findall(r'\d', zipcode)) > 4:
            errors.add('304')  #Zipcode error: more than 4 digits
        if len(re.findall(r'\d', zipcode)) < 4:
            errors.add('305')  #Zipcode error: less than 4 digits
        if zipcode.startswith(' ') or zipcode.endswith(' ') or "  " in zipcode:
            errors.add('302')  #Zipcode error: unnecessary spaces
        if not re.search(r'^\d+$',zipcode):
            errors.add('303')  #Zipcode error: invalid characters
        elif not (999 < int(zipcode) <= 9265):
            errors.add('306')  #Zipcode error: out of range

    # City errors
    if pd.isna(city) or city is None or city.strip() == "" or city.strip() == "/" :
        errors.add('401')  # City error: no information given
    else:
        if city.startswith(' ') or city.endswith(' ') or "  " in city:
            errors.add('402')  #City error: unnecessary spaces
        if re.search(r'[^a-zA-ZčČšŠžŽ\s]', city):
            errors.add('404')  #City error: invalid characters
        if re.search(r'\d', city):
            errors.add('403') # City error: contains digits
        if re.search(r'\b(?!(?:' + '|'.join(allowed_abbreviations_city) + r')\.)\w+\.', city, flags=re.IGNORECASE): 
            errors.add('405')  #City error: invalid abbreviations
        if city:
            components = [comp.replace(',', '').upper() 
                        for comp in re.split(r'\s+', city) if comp]
            prev_comp = None
            for comp in components:
                if prev_comp and prev_comp == comp:
                    errors.add('406')    # City error: consecutive duplicates detected
                    break 
                prev_comp = comp

    return ','.join(sorted(errors))

# TESTING

customer_data = "src/processed_data/customer_data_with_errors.xlsx"

df = pd.read_excel(customer_data)

df["DETECTED_ERRORS"] = df.apply(lambda row: detect_address(
    row["STREET"], row["HOUSE_NUMBER"], row["POSTAL_CODE"], row["POSTAL_CITY"]
), axis=1)

# print(df.head())

df.to_excel("src/processed_data/01_customer_data_with_detected_errors.xlsx", index=False)
print("Detection of address errors completed!")