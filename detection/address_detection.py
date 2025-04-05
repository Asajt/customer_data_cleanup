import pandas as pd
import re
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.errors_utils import should_detect, load_error_config

error_config = load_error_config()

def detect_address_errors(street, street_number, zipcode, city):
    """Detects errors in several address components based on various criteria.

    This function checks for missing data, unnecessary spaces, invalid characters,
    formatting issues, duplicates, and the presence of multiple components in a single field.

    Args:
        street (str): The street name to be checked.
        street_number (str): The street number to be checked.
        zipcode (str): The postal code to be checked.
        city (str): The city name to be checked.

    Returns:
        dict: A dictionary containing detected errors for each address component.
        The keys are:
            - "street_detected_errors": A list of error codes for the street.
            - "street_number_detected_errors": A list of error codes for the street number.
            - "zipcode_detected_errors": A list of error codes for the zipcode.
            - "city_detected_errors": A list of error codes for the city.
    """

    # Check for NaN values and convert them to empty strings
    street = "" if pd.isna(street) else str(street)
    street_number = "" if pd.isna(street_number) else str(street_number)
    zipcode = "" if pd.isna(zipcode) else str(zipcode)
    city = "" if pd.isna(city) else str(city)

    street_errors = set()
    street_number_errors = set()
    zipcode_errors = set()
    city_errors = set()
    
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
    # 4101 Check for missing data
    rule_condition = (pd.isna(street) or street is None or street.strip() == "" or street.strip() == "/" )
    if should_detect('4101', error_config):
        if rule_condition:
            street_errors.add('4101') 
    
        else:
            # 4111 Starts with number
            rule_condition = (re.search(r'^\d',street))
            if should_detect('4111', error_config):
                if rule_condition:
                    street_errors.add('4111')
            
            # 4102 Check for unnecessary spaces
            rule_condition = (street.startswith(' ') or street.endswith(' ') or "  " in street)
            if should_detect('4102', error_config):
                if rule_condition:
                    street_errors.add('4102')
            
            # 4106 Contains variation of BŠ
            rule_condition = (any(re.search(r'\b' + re.escape(pattern) + r'\b', street) for pattern in hn_patterns))
            if should_detect('4106', error_config):
                if rule_condition:
                    street_errors.add('4106')
            
            # 4103 Check for invalid characters
            rule_condition = (not re.search(r'^[a-zA-ZčćšžČĆŠŽ\d\s\.,-/]+$', street) or '//' in street)
            if should_detect('4103', error_config):
                if rule_condition:
                    street_errors.add('4103')
            
            # !!!  Formatting issues (check whether the case of letters is correct) 
            
            # 4107 Check for invalid abbreviations
            rule_condition = (re.search(r'(?<!\d)\.',street) and \
                re.search(r'\b(?!(?:' + '|'.join(allowed_abbreviations_street) + r')\.)\w+\.', street, flags=re.IGNORECASE))
            if should_detect('4107', error_config):
                if rule_condition:
                    street_errors.add('4107') 
            
            # 4109 Only numbers
            rule_condition = (not any(char.isalpha() for char in street))
            if should_detect('4109', error_config):
                if rule_condition:
                    street_errors.add('4109')
            
            # 4110 Check for (consecutive) duplicates
            if street:
                components = [comp.replace(',', '').upper() 
                            for comp in re.split(r'\s+', street) if comp]
                prev_comp = None
                for comp in components:
                    rule_condition = (prev_comp and prev_comp == comp)
                    if should_detect('4110', error_config):
                        if rule_condition:
                            street_errors.add('4110')
                            break 
                    prev_comp = comp
            
            # 4105 Contains house number
            rule_condition = re.search(r'\d+[A-Za-zČčŠšŽž]{0,3}(\/?|\.?|\s?)[A-Za-zČčŠšŽž]{0,3}$', street)
            if should_detect('4105', error_config):
                if rule_condition:
                    street_errors.add('4105')
                    
            # !!! cannot contain digit at the end
            
            # 4112 Check for invalid digit in street
            skip_if_condition = not '4105' in street_errors
            rule_condition = re.search(r'\d+$', street)
            if should_detect('4112', error_config):
                if skip_if_condition:
                    if rule_condition:
                        street_errors.add('4112')
                    
            # 4108 Check for no space after full stop
            skip_if_condition = (any(code in street_errors for code in ["4105", "4107"]))
            rule_condition = (street and re.search(r'\.(?![\s\W])',street))
            if should_detect('4108', error_config):
                if skip_if_condition:
                    if rule_condition:
                        street_errors.add('4108') 
        
            # 4113 Check for invalid digit in street
            skip_if_condition = (not '4105' in street_errors)
            rule_condition = ((re.search(r'\d+(?![.\d])', street)) and not \
                (re.search(r'25\s+TALCEV',street))) #edina ulica, ki nima pike po številki 2024/03/12 
            if should_detect('4113', error_config):
                if skip_if_condition:
                    if rule_condition:
                        street_errors.add('4113') 
            
            # !!! replacing šćčž to scz

    # Street_number errors 
    # 4201 Check for missing data
    rule_condition = (pd.isna(street_number) or street_number is None or street_number.strip() == "" or street_number.strip() == "/")
    if should_detect('4201', error_config):
        if rule_condition:
            street_number_errors.add('4201') 
        else:
            
            # 4208 Check for roman numerals
            rule_condition = (re.search(r'\b(?:' + '|'.join(roman_numbers) + r')\d*\b', street_number, flags=re.IGNORECASE))
            if should_detect('4208', error_config):
                if rule_condition:
                    street_number_errors.add('4208')  
            
            # 4202 Check for unnecessary spaces
            rule_condition = (street_number.startswith(' ') or street_number.endswith(' ') or "  " in street_number)
            if should_detect('4202', error_config):
                if rule_condition:
                    street_number_errors.add('4202')
            
            # 4213 contains BŠ as well as a number
            rule_condition = (any(pattern in street_number for pattern in hn_patterns) and re.search(r'\d', street_number))
            if should_detect('4213', error_config):
                if rule_condition:
                    street_number_errors.add('4213') 
            
            # 4203 Contains variation of BŠ
            skip_if_condition = (not '4213' in street_number_errors)
            rule_condition = (any(pattern in street_number for pattern in hn_patterns))
            if should_detect('4203', error_config):
                if skip_if_condition:
                    if rule_condition:
                        street_number_errors.add('4203')  
            
            # 4205 ends with full stop
            skip_if_condition = (not '4203' in street_number_errors)
            rule_condition = (street_number.endswith('.') and re.search(r'\d', street_number))
            if should_detect('4205', error_config):
                if skip_if_condition:
                    if rule_condition:
                        street_number_errors.add('4205') 
            
            # 4210 More than one number present
            rule_condition = (len(re.findall(r'\d+', street_number)) > 1)
            if should_detect('4210', error_config):
                if rule_condition:
                    street_number_errors.add('4210')
            
            # 4204 Check for no house number
            skip_if_condition = (not any(code in street_number_errors for code in ["4202", "4203", "4208"]))
            rule_condition = (not (re.search(r'\d', street_number)) or (re.search(r'^[^1-9]*0[^1-9]*$', street_number)))
            if should_detect('4204', error_config):
                if skip_if_condition:
                    if rule_condition:
                        street_number_errors.add('4204') 
            
            # 4208 Does not start with digit
            skip_if_condition = not any(code in street_number_errors for code in ["4202", "4203", "4204", "4208"])
            rule_condition = re.search(r'^[^0-9]',street_number)
            if should_detect('4208', error_config):
                if skip_if_condition:
                    if rule_condition:
                        street_number_errors.add('4208')  # Street number error: does not start with digit
            
            # 4211 CHeck for 4 digits
            skip_if_condition = (not '4204' in street_number_errors)
            rule_condition = (re.findall(r'\d{4,}', street_number))
            if should_detect('4211', error_config):
                if skip_if_condition:
                    if rule_condition:
                        street_number_errors.add('4211') 
            
            # 4207 Spacing / invalid characters between components
            skip_if_condition = not any(code in street_number_errors for code in ["4203", "4210", "4208", "4211"])
            rule_condition = re.search(r'(\d+)(\/|(\s\/)|(\s\/\s)|\s|\.|\,|\-)([a-zA-ZččšžĆČŠŽ]{1,2})$', street_number)
            if should_detect('4207', error_config):
                if skip_if_condition:
                    if rule_condition:
                        street_number_errors.add('4207')
            
            # 4206 Leading 0
            skip_if_condition = (not '4204' in street_number_errors)
            rule_condition = (re.search(r'\b0\s*\d+', street_number))
            if should_detect('4206', error_config):
                if skip_if_condition:
                    if rule_condition:
                        street_number_errors.add('4206') 
            
            # 4205 Invalid combination
            skip_if_condition = (not street_number_errors)
            rule_condition = (not re.search(r'^\d{1,3}[A-Za-zČčŠšŽž]{0,2}$', street_number))
            if should_detect('4205', error_config):
                if skip_if_condition:
                    if rule_condition:
                        street_number_errors.add('4205')  # Invalid combination

    # Zipcode errors     
    # 4301 Check for missing data
    rule_condition = (pd.isna(zipcode) or zipcode is None or zipcode.strip() == "")
    if should_detect('4301', error_config):
        if rule_condition:
            zipcode_errors.add('4301')
        else:
            # 4305 Check for more than 4 digits
            rule_condition = (len(re.findall(r'\d', zipcode)) > 4)
            if should_detect('4305', error_config):
                if rule_condition:
                    zipcode_errors.add('4305')
                
            # 4304 Check for less than 4 digits
            rule_condition = len(re.findall(r'\d', zipcode)) < 4
            if should_detect('4304', error_config):
                if rule_condition:
                    zipcode_errors.add('4304')
                
            # 4302 Check for unnecessary spaces
            rule_condition = (zipcode.startswith(' ') or zipcode.endswith(' ') or "  " in zipcode)
            if should_detect('4302', error_config):
                if rule_condition:
                    zipcode_errors.add('4302') 
                
            # 4303 Check for invalid characters
            skip_if_condition = not '4302' in zipcode_errors
            rule_condition = (not re.search(r'^\d+$',zipcode))
            if should_detect('4303', error_config):    
                if skip_if_condition:
                    if rule_condition:
                        zipcode_errors.add('4303') 
                
            # 4306 Check for invalid value
            elif should_detect('4307', error_config):
                skip_if_condition = (not zipcode_errors)
                rule_condition = (not (999 < int(zipcode) <= 9265) and '4305' not in zipcode_errors and '4304' not in zipcode_errors)
                if skip_if_condition:
                    if rule_condition:
                        zipcode_errors.add('4307') 

    # City errors
    # 4401 Check for missing data
    rule_condition = (pd.isna(city) or city is None or city.strip() == "" or city.strip() == "/")
    if should_detect('4401', error_config):
        if rule_condition:
            city_errors.add('4401')
        else:
            # 4404 Check for unnecessary spaces
            rule_condition = (city.startswith(' ') or city.endswith(' ') or "  " in city)
            if should_detect('4402', error_config):
                if rule_condition:
                    city_errors.add('4402')  
                
            # 4402 Check for invalid characters
            rule_condition = (re.search(r'[^a-zA-ZčČšŠžŽ\s]', city))
            if should_detect('4403', error_config):
                if rule_condition:
                    city_errors.add('4403')  
            
            # 4405 Check for digits
            rule_condition = (re.search(r'\d', city))
            if should_detect('4405', error_config):
                if rule_condition:
                    city_errors.add('4405')
                
            # 4406 Check for invalid abbreviations
            rule_condition = (re.search(r'\b(?!(?:' + '|'.join(allowed_abbreviations_city) + r')\.)\w+\.', city, flags=re.IGNORECASE))
            if should_detect('4406', error_config):
                if rule_condition:
                    city_errors.add('4406') 
                
            # 4407 Check for (consecutive) duplicates
            if city:
                components = [comp.replace(',', '').upper() 
                            for comp in re.split(r'\s+', city) if comp]
                prev_comp = None
                for comp in components:
                    rule_condition = (prev_comp and prev_comp == comp)
                    if should_detect('4407', error_config):
                        if rule_condition:
                            city_errors.add('4407')
                            break 
                        prev_comp = comp

    # return ','.join(sorted(errors))
    return {
        "street_detected_errors": sorted(street_errors),
        "street_number_detected_errors": sorted(street_number_errors),
        "zipcode_detected_errors": sorted(zipcode_errors),
        "city_detected_errors": sorted(city_errors)
    }

if __name__ == "__main__":
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    errors_df = df.apply(
        lambda row: pd.Series(detect_address_errors(row["STREET"], row["HOUSE_NUMBER"], row["POSTAL_CODE"], row["POSTAL_CITY"])),
        axis=1
    )

    # Convert lists to comma-separated strings just for saving
    df["street_detected_errors"] = errors_df["street_detected_errors"].apply(lambda x: ", ".join(x))
    df["house_number_detected_errors"] = errors_df["street_number_detected_errors"].apply(lambda x: ", ".join(x))
    df["POSTAL_CODE_detected_errors"] = errors_df["zipcode_detected_errors"].apply(lambda x: ", ".join(x))
    df["POSTAL_CITY_detected_errors"] = errors_df["city_detected_errors"].apply(lambda x: ", ".join(x))

    # choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", 
        "STREET", "street_detected_errors",
        "HOUSE_NUMBER", "house_number_detected_errors",
        "POSTAL_CODE", "POSTAL_CODE_detected_errors",
        "POSTAL_CITY", "POSTAL_CITY_detected_errors"
    ]
    df = df[columns_to_keep]
    
    # Save the result
    df.to_excel("src/processed_data/02_detected_address_errors.xlsx", index=False)
    print("Detection of address errors completed and saved!")
