import pandas as pd
import numpy as np
import random
import regex as re

# Set seed for reproducibility
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

# ============================
# **HELPER FUNCTION: LOG ERRORS**
# ============================
def log_error(df, row_id, error_id):
    """ Append error ID to INTRODUCED_ERRORS column """
    if df.at[row_id, "INTRODUCED_ERRORS"]:
        df.at[row_id, "INTRODUCED_ERRORS"] += f", {error_id}"
    else:
        df.at[row_id, "INTRODUCED_ERRORS"] = str(error_id)


# ============================
# **APPLY ERRORS FUNCTION**
# ============================
def apply_errors(df):
    """
    Introduces errors into the dataset and tracks them in the 'INTRODUCED_ERRORS' column.
    
    Parameters:
    df (pd.DataFrame): The dataset containing customer data.

    Returns:
    None (Modifies the dataframe in place and tracks applied errors)
    """
    
    df = df.astype(str)
    
    df['INTRODUCED_ERRORS'] = ""  # Initialize the error tracking column
    
    for index in df.index:
        # ============================
        # **FIRST_NAME ERRORS**
        # ============================
        current_value = df.at[index, "FIRST_NAME"]
        if np.random.rand() < 0.15:
            new_value = current_value  # Keep the original value until an error is applied
            # ERROR 1101 - Missing Data
            if random.random() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""
                if new_value != current_value:
                    log_error(df, index, "1101")

            else:          
                # ERROR 1102 - Unnecessary Spaces
                if random.random() < 0.03:
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                    if new_value != current_value:
                        log_error(df, index, "1102")
                        current_value = new_value


                # ERROR 1103 - Invalid Characters (replace letters with numbers)
                if random.random() < 0.02:
                    if np.random.rand() < 0.5:
                        new_value = str(current_value).replace("a", "@").replace("o", "0").replace("e", "3").replace("i", "1")
                    else:
                        encoding_map = {
                            "a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú",
                            "A": "Á", "E": "É", "I": "Í", "O": "Ó", "U": "Ú",
                            "c": "č", "s": "š", "z": "ž"
                        }
                        new_value = "".join(encoding_map.get(char, char) for char in current_value)
                    if new_value != current_value:
                        log_error(df, index, "1103")
                        current_value = new_value
                
                # ERROR 1104 - Formatting Issues
                if random.random() < 0.03:
                    if np.random.rand() < 0.5:
                        new_value = random.choice([current_value.upper(), current_value.lower(), current_value.capitalize()])
                    else:
                        # Randomly change the upper/lower case of letters
                        new_value = ''.join(random.choice([char.upper(), char.lower()]) for char in current_value)  # FIXED
                    if new_value != current_value:
                        log_error(df, index, "1104")
                        current_value = new_value
                                
                # ERROR 1105 - Duplicates
                if random.random() < 0.01:
                    new_value = f"{current_value} {current_value}"  # Duplicates error
                    if new_value != current_value:
                        log_error(df, index, "1105")
                        current_value = new_value
                    
                # ERROR 1106 - Two names in one field
                if random.random() < 0.01:
                    second_name = random.choice(["Marija", "Janez", "Ana", "Marko"])
                    new_value = f"{current_value} in {second_name}"  # Two names in one field error
                    if new_value != current_value:
                        log_error(df, index, "1106")
                        current_value = new_value

                # ERROR 1107 - Initials
                if random.random() < 0.01:
                    initials = ''.join([name[0].upper() + '.' for name in current_value.split()])
                    new_value = initials if len(current_value.split()) == 1 else current_value
                    if new_value != current_value:
                        log_error(df, index, "1107")
                        current_value = new_value

                # ERROR 1108 - Replace š, č, ž, ć with s, c, z, c
                if random.random() < 0.02:
                    replacement_map = {"š": "s", "č": "c", "ž": "z", "ć": "c", "Š": "S", "Č": "C", "Ž": "Z", "Ć": "C"}
                    new_value = ''.join(replacement_map.get(char, char) for char in current_value)
                    if new_value != current_value:
                        log_error(df, index, "1108")
                        current_value = new_value
                
            df.at[index, "FIRST_NAME"] = new_value  # Apply error to the column

        # ============================
        # **LAST_NAME ERRORS**
        # ============================
        current_value = df.at[index, "LAST_NAME"]
        
        if np.random.rand() < 0.10:  
            new_value = current_value  # Keep the original value until an error is applied
            # ERROR 1201 - Missing Data
            if random.random() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""  # Missing data error
                if new_value != current_value:
                    log_error(df, index, "1201")
                
            else:

                # ERROR 1202 - Unnecessary Spaces
                if random.random() < 0.03:
                    random_choice = random.choice(["leading", "trailing", "double"])
                    if random_choice == "leading":
                        new_value = " " + current_value
                    elif random_choice == "trailing":
                        new_value = current_value + " "  
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)
                    if new_value != current_value:
                        log_error(df, index, "1202")
                        current_value = new_value

                # ERROR 1203 - Invalid Characters
                if random.random() < 0.02:
                    if np.random.rand() < 0.5:
                        new_value = str(current_value).replace("a", "@").replace("o", "0").replace("e", "3").replace("i", "1")
                    else:
                        encoding_map = {
                            "a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú",
                            "A": "Á", "E": "É", "I": "Í", "O": "Ó", "U": "Ú",
                            "c": "č", "s": "š", "z": "ž"
                        }
                        new_value = "".join(encoding_map.get(char, char) for char in current_value)
                    if new_value != current_value:
                        log_error(df, index, "1203")
                        current_value = new_value
                    
                # ERROR 1204 - Formatting Issues
                if random.random() < 0.03:
                    if np.random.rand() < 0.5:
                        new_value = random.choice([current_value.upper(), current_value.lower(), current_value.capitalize()])
                    else:
                        # Randomly change the upper/lower case of letters
                        new_value = ''.join(random.choice([char.upper(), char.lower()]) for char in current_value)
                    if new_value != current_value:
                        log_error(df, index, "1204")
                        current_value = new_value
                    
                # ERROR 1205 - Duplicates
                if random.random() < 0.01:
                    new_value = f"{current_value} {current_value}"  # Duplicates error
                    if new_value != current_value:
                        log_error(df, index, "1205")
                        current_value = new_value
                    
                # ERROR 1206 - Replace š, č, ž, ć with s, c, z, c
                if random.random() < 0.02:
                    replacement_map = {"š": "s", "č": "c", "ž": "z", "ć": "c", "Š": "S", "Č": "C", "Ž": "Z", "Ć": "C"}
                    new_value = ''.join(replacement_map.get(char, char) for char in current_value)
                    if new_value != current_value:
                        log_error(df, index, "1206")
                        current_value = new_value
                    
            df.at[index, "LAST_NAME"] = new_value  # Apply error to the column
            

        # ============================
        # **EMAIL ERRORS**
        # ============================
        current_value = df.at[index, "EMAIL"]
        
        invalid_domains = [
        "gmial.com", "gmaiul.com", "gmail.cm", "telemac.com", "hot*mail.com",
        "sioln.et", "sio.net", "sloveniamali.com", "email.si", "t-2.nt", "amis.nte"
        ]
        
        
        if np.random.rand() < 0.20:  # 5% chance for errors
            new_value = current_value  # Keep the original value until an error is applied
            # ERROR 2101 - Missing Data
            if np.random.rand() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""
                if new_value != current_value:
                    log_error(df, index, "2101")
            else:

                # ERROR 2102 - Unnecessary Spaces
                if random.random() < 0.03:
                    random_choice = random.choice(["leading", "trailing", "double"])
                    if random_choice == "leading":
                        new_value = " " + current_value
                    elif random_choice == "trailing":
                        new_value = current_value + " "  
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)
                    if new_value != current_value:
                        log_error(df, index, "2102")
                        current_value = new_value

                # ERROR 2103 - Invalid Characters & Encoding Issues
                if random.random() < 0.03:
                    encoding_map = {"č": "c", "š": "s", "ž": "z"}
                    modified_email = "".join(encoding_map.get(char, char) for char in current_value)
                    new_value = modified_email.replace(".", ",").replace("@", "#")
                    if new_value != current_value:
                        log_error(df, index, "2103")
                        current_value = new_value
                
                # ERROR 2104 - Formatting Issue
                if np.random.rand() < 0.03:
                    new_value = current_value.replace("@", "#").replace(".", "..")
                    if new_value != current_value:
                        log_error(df, index, "2104")
                        current_value = new_value
                    
                # ERROR 2105 - Possibly Two Emails
                if np.random.rand() < 0.01:
                    extra_email = f"user{random.randint(1, 100)}@example.com"
                    new_value = f"{current_value}, {extra_email}"    
                    if new_value != current_value:
                        log_error(df, index, "2105")
                        current_value = new_value
                    
                # ERROR 2106 - Possibly Invalid Domain
                if random.random() < 0.02:
                    local_part = current_value.split("@")[0]
                    new_value = f"{local_part}@{random.choice(invalid_domains)}"
                    if new_value != current_value:
                        log_error(df, index, "2106")
                        current_value = new_value
                
            df.at[index, "EMAIL"] = new_value  # Apply error to the column



        # ============================
        # **PHONE_NUMBER ERRORS**
        # ============================
        current_value = df.at[index, "PHONE_NUMBER"]
        
        if np.random.rand() < 0.30:  # 5% chance for errors
            new_value = current_value  # Keep the original value until an error is applied
            # ERROR 3101 - Missing Data
            if np.random.rand() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""
                if new_value != current_value:
                    log_error(df, index, "3101")
                
            else:

                # ERROR 3102 - Unnecessary Spaces
                if random.random() < 0.03:
                    random_choice = random.choice(["leading", "trailing", "double"])
                    if random_choice == "leading":
                        new_value = " " + current_value
                    elif random_choice == "trailing":
                        new_value = current_value + " "  
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)
                    if new_value != current_value:
                        log_error(df, index, "3102")
                        current_value = new_value

                # ERROR 3103 - Invalid Characters
                if np.random.rand() < 0.04:
                    new_value = current_value.replace("0", "O").replace("1", "I")  # Replace digits with letters
                    if new_value != current_value:
                        log_error(df, index, "3103")
                        current_value = new_value

                # ERROR 3104 - Formatting Issues
                if np.random.rand() < 0.30:
                    new_value = random.choice([
                        current_value.replace("00386", "+386"),  
                        current_value.replace("00386", ""), 
                        current_value.replace("00386", "0"),
                        current_value.replace("00386", "+00386")
                    ])
                    if new_value != current_value:
                        log_error(df, index, "3104")
                        current_value = new_value
                    
                # ERROR 3105 - Too Many Digits
                if random.random() < 0.01:
                    new_value = current_value + str(random.randint(0, 9))  # Append a random digit
                    if new_value != current_value:
                        log_error(df, index, "3105")
                        current_value = new_value

                # ERROR 3106 - Too Few Digits
                if np.random.rand() < 0.03:
                    num_digits_to_remove = random.randint(1, 3)  # Remove 1 to 3 digits randomly
                    new_value = current_value[:-num_digits_to_remove]
                    if new_value != current_value:
                        log_error(df, index, "3106")
                        current_value = new_value

                # ERROR 3107 - Two Phone Numbers
                if np.random.rand() < 0.02:
                    extra_number = f"0038631{random.randint(100000, 999999)}"
                    new_value = f"{current_value}, {extra_number}"
                    if new_value != current_value:
                        log_error(df, index, "3107")
                        current_value = new_value

                # ERROR 3108 - Different country format
                if np.random.rand() < 0.05:
                    alternative_country_codes = ["+385", "+49", "+33", "+44", "+30", "00385", "0049", "0033", "0044", "0030"]  # Croatia, Germany, France, UK, Greece
                    new_country_code = random.choice(alternative_country_codes)
                    new_value = current_value.replace("00386", new_country_code)
                    if new_value != current_value:
                        log_error(df, index, "3108")
                        current_value = new_value
                
            df.at[index, "PHONE_NUMBER"] = new_value  # Apply error to the column
        
        # ============================
        # **STREET ERRORS**
        # ============================
        current_value = df.at[index, "STREET"]
        
        # 5% chance for errors
        if np.random.rand() < 0.10:
            new_value = current_value  # Keep the original value until an error is applied
            # ERROR 4101 - Missing Data
            if random.random() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""  # Missing Data error
                if new_value != current_value:
                    log_error(df, index, "4101")
            
            else:
                    
                # ERROR 4102 - Unnecessary Spaces
                if np.random.rand() < 0.05:
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                    if new_value != current_value:
                        log_error(df, index, "4102")
                        current_value = new_value                    
                
                # ERROR 4103 - Invalid Characters
                if np.random.rand() < 0.08:
                    invalid_chars = ["◊", "�", "ß", "ø", "ç", "@", "#", "%", "&", "*", "~", "^", "!", "?", "_", "|", "/", "\\", "="]
                    eligible_chars = ["č", "š", "ž", "ć", "Č", "Š", "Ž", "Ć"]
                    new_value = ''.join(random.choice(invalid_chars) if char in eligible_chars else char for char in current_value)
                    if new_value != current_value:
                        log_error(df, index, "4103")
                        current_value = new_value
                
                # ERROR 4108 - No Space After Full Stop
                if re.search(r'\.', str(current_value)):  
                    if np.random.rand() < 0.4:
                        new_value = current_value.replace(". ", ".")
                        if new_value != current_value:
                            log_error(df, index, "4108")
                            current_value = new_value
                            
                # ERROR 4104 - Formatting Issues
                if random.random() < 0.03:
                    if np.random.rand() < 0.5:
                        new_value = random.choice([current_value.upper(), current_value.lower(), current_value.capitalize()])
                    else:
                        # Randomly change the upper/lower case of letters
                        new_value = ''.join(random.choice([char.upper(), char.lower()]) for char in current_value)
                    if new_value != current_value:
                        log_error(df, index, "4104")
                        current_value = new_value

                # ERROR 4111 - Starts with Digit
                if re.search(r'\d+', current_value):
                    if np.random.rand() < 0.08:
                        match = re.search(r'\d', current_value) 
                        digit_index = match.start()  # Get its position
                        new_value = current_value[digit_index:]  # Keep only from the first digit onwards
                        if new_value != current_value:
                            log_error(df, index, "4111")
                            current_value = new_value
                    elif np.random.rand() < 0.08:
                        match = re.search(r'\d+', current_value) 
                        digit_index = match.start() + len(match.group())
                        new_value = current_value[:digit_index].strip() 
                        if new_value != current_value:
                            log_error(df, index, "4112")
                            current_value = new_value

                # ERROR 4105 - Contains House Number
                if np.random.rand() < 0.1:
                    house_number_options = [
                        str(df.at[index, "HOUSE_NUMBER"]),  # Actual house number
                        str(random.randint(1, 999)),  # Random number
                        random.choice(["BŠ", "NH", "B$", "BS", "N.H.", "B.Š."]),  # Slovene indicator
                    ]
                    new_value = f"{current_value} {random.choice(house_number_options)}"
                    if new_value != current_value:
                        log_error(df, index, "4105")
                        current_value = new_value

                # ERROR 4106 - Contains Variation of BŠ
                if np.random.rand() < 0.01:
                    terms = ("BŠ", "NH", "B$", "BS", "N.H.", "B.Š.")
                    new_value = current_value + f" {random.choice(terms)}"
                    if new_value != current_value:
                        log_error(df, index, "4106")
                        current_value = new_value

                # ERROR 4107 - Invalid Abbreviations
                if np.random.rand() < 0.25:
                    abbreviation_map = {
                        "ulica": ["ul.", "u."],
                        "cesta": ["ce.", "c."]}

                    for full, abbrs in abbreviation_map.items():
                        if full in current_value:  # If 'ulica' or 'cesta' exists
                            chosen_abbr = random.choice(abbrs)  # Randomly select an abbreviation
                            new_value = current_value.replace(full, chosen_abbr, 1)  # Replace first occurrence
                    if new_value != current_value:
                        log_error(df, index, "4107")
                        current_value = new_value

                # ERROR 4109 - Only Numbers
                if np.random.rand() < 0.01:
                    new_value = "".join([str(random.randint(1, 9)) for _ in range(3)])
                    if new_value != current_value:
                        log_error(df, index, "4109")
                        current_value = new_value

                # ERROR 4110 - Duplicates
                if np.random.rand() < 0.01:
                    duplicate_type = random.choice(["full", "partial"])
                    if duplicate_type == "full":
                        new_value = f"{current_value} {current_value}"
                    else:
                        words = current_value.split()
                        if len(words) > 1:
                            new_value = " ".join(words + [words[-1]])
                    if new_value != current_value:
                        log_error(df, index, "4110")
                        current_value = new_value

                # ERROR 4113 - Invalid Digit in Street
                if re.search(r'\d+\.', current_value):
                    if np.random.rand() < 0.05:
                        new_value = re.sub(r'(\d+)\.', r'\1', current_value)
                        log_error(df, index, "4113")
                        current_value = new_value

                # ERROR 4114 - Replace š, č, ž, ć with s, c, z, c
                if np.random.rand() < 0.3:
                    replacement_map = {"š": "s", "č": "c", "ž": "z", "ć": "c", "Š": "S", "Č": "C", "Ž": "Z", "Ć": "C"}
                    new_value = ''.join(replacement_map.get(char, char) for char in current_value)
                    if new_value != current_value:
                        log_error(df, index, "4114")
                        current_value = new_value
     
            df.at[index, "STREET"] = new_value  # Apply error to the column

        # ============================
        # **HOUSE_NUMBER ERRORS**
        # ============================
        current_value = df.at[index, "HOUSE_NUMBER"]
        
        # 5% chance for errors
        if np.random.rand() < 0.15:
            new_value = current_value  # Keep the original value until an error is applied

            # ERROR 4201 - Missing Data
            if np.random.rand() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""
                if new_value != current_value:
                    log_error(df, index, "4201")

            else:

                # ERROR 4202 - Unnecessary Spaces (Leading, Trailing, Double)
                if np.random.rand() < 0.05:
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                    else:
                        new_value = current_value
                    if new_value != current_value:
                        log_error(df, index, "4202")
                        current_value = new_value
                        
                # ERROR 4203 - Contains Variation of BŠ
                if np.random.rand() < 0.01:
                    new_value = random.choice(["BŠ", "NH", f"BŠ {current_value}", f"NH {current_value}"])
                    if new_value != current_value:
                        log_error(df, index, "4203")
                        current_value = new_value

                # ERROR 4204 - No House Number
                if np.random.rand() < 0.01:
                    new_value = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                    if new_value != current_value:
                        log_error(df, index, "4204")
                        current_value = new_value


                # ERROR 4205 - Invalid Combination
                if np.random.rand() < 0.01:
                    # Identify number and letter parts using regex
                    match = re.match(r"(\d+)([A-Za-z]?)", current_value)  # Extract number and optional letter
                    if match:
                        num_part, letter_part = match.groups()
                        if letter_part:  # If there is a letter, introduce a random separator
                            separator = random.choice([" ", "-", "/"])
                            new_value = f"{num_part}{separator}{letter_part}"
                        else:  # If no letter part, introduce one and add a separator
                            new_value = f"{num_part}{random.choice(['A', 'B'])}"
                    if new_value != current_value:
                        log_error(df, index, "4205")
                        current_value = new_value

                # ERROR 4206 - Leading 0
                if np.random.rand() < 0.01:
                    if not current_value.startswith("0"):  # Avoid adding if already has leading zero
                        zeros_to_add = random.choice(["0", "00"])  # Randomly choose 1 or 2 zeros
                        new_value = zeros_to_add + current_value
                    if new_value != current_value:
                        log_error(df, index, "4206")
                        current_value = new_value

                # ERROR 4207 - Spacing Between Components
                if np.random.rand() < 0.01:
                    new_value = current_value.replace(" ", "").replace(".", "").replace("/", "")
                    if new_value != current_value:
                        log_error(df, index, "4207")
                        current_value = new_value

                # ERROR 4208 - Contains Roman Numerals (1%)
                if np.random.rand() < 0.01:
                    roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
                    roman_choice = random.choice(roman_numerals)

                    # Randomly decide whether to replace or prepend the house number
                    if random.random() < 0.5:
                        new_value = f"{roman_choice} {current_value}"  # E.g., "IV 5"
                    else:
                        new_value = roman_choice  # E.g., "IV"
                    if new_value != current_value:
                        log_error(df, index, "4208")
                        current_value = new_value

                # ERROR 4209 - Ends with full stop
                if np.random.rand() < 0.01:
                    new_value = current_value + '.'
                    if new_value != current_value:
                        log_error(df, index, "4209")
                        current_value = new_value

                # ERROR 4210 - More than one number present
                if np.random.rand() < 0.01:
                    new_value = current_value + f" {random.randint(1, 99)}"
                    if new_value != current_value:
                        log_error(df, index, "4210")
                        current_value = new_value

                # ERROR 4211 - Does not start with digit
                if np.random.rand() < 0.01:
                    prefixes = ["St.", "HS", "HŠ", "A", "B", "H", "št.", "Stanovanje", "st."]
                    new_value = random.choice(prefixes) + " " + current_value
                    if new_value != current_value:
                        log_error(df, index, "4211")
                        current_value = new_value

                # ERROR 4212 - More than 4 digits
                if np.random.rand() < 0.01 and current_value.isdigit() and 2 <= len(current_value) <= 3:
                    new_value = current_value + str(random.randint(10, 99)) 
                    if new_value != current_value:
                        log_error(df, index, "4212")
                        current_value = new_value

            df.at[index, "HOUSE_NUMBER"] = new_value  # Apply error to the column

        # ============================
        # **POSTAL_CODE ERRORS**
        # ============================
        current_value = df.at[index, "POSTAL_CODE"]
        
        # 5% chance for errors
        if np.random.rand() < 0.08:
            new_value = current_value  # Keep the original value until an error is applied
            
            # ERROR 4301 - Missing Data (5%)
            if np.random.rand() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""
                if new_value != current_value:
                    log_error(df, index, "4301")

            else:
                    
                # ERROR 4302 - Unnecessary Spaces (Leading, Trailing, Double)
                if np.random.rand() < 0.05:
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                    if new_value != current_value:
                        log_error(df, index, "4302")
                        current_value = new_value
                    
                # ERROR 4303 - Invalid Characters 
                if np.random.rand() < 0.01:
                    new_value = current_value.replace("0", random.choice(["-", "/", "*", "X"]), 1)
                    if new_value != current_value:
                        log_error(df, index, "4303")
                        current_value = new_value

                # ERROR 4304 - Less than 4 Digits (1%)
                if np.random.rand() < 0.01:
                    new_value = current_value[:random.randint(1, 3)]  # Trim to <4 digits
                    if new_value != current_value:
                        log_error(df, index, "4304")
                        current_value = new_value

                # ERROR 4305 - More than 4 Digits (1%)
                if np.random.rand() < 0.01:
                    new_value = current_value + str(random.randint(0, 9))  # Extend with extra digit
                    if new_value != current_value:
                        log_error(df, index, "4305")
                        current_value = new_value

                # ERROR 4306 - Contains Letters 
                if np.random.rand() < 0.01:
                    postal_city = df.at[index, "POSTAL_CITY"] if "POSTAL_CITY" in df.columns else "Ljubljana"
                    if random.random() < 0.9:
                        new_value = f"{current_value} {postal_city}"
                    elif random.random() < 0.2:
                        new_value = f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{current_value}"
                    # Fallback if postal_city is missing or empty
                    elif random.random() < 0.3:
                        new_value = f"Ljubljana {current_value}"
                    if new_value != current_value:
                        log_error(df, index, "4306")
                        current_value = new_value

                
                
                # ERROR 4307 - Invalid Value
                if np.random.rand() < 0.02:
                    new_value = random.choice(["ABC", "0000", "99999"])
                    if new_value != current_value:
                        log_error(df, index, "4307")
                        current_value = new_value

                
            df.at[index, "POSTAL_CODE"] = new_value  # Apply error to the column
            
        # ============================
        # **POSTAL_CITY ERRORS**
        # ============================
        current_value = df.at[index, "POSTAL_CITY"]
        
        # 5% chance for errors
        if np.random.rand() < 0.08:
            new_value = current_value  # Keep the original value until an error is applied

            # ERROR 4401 - Missing Data (5%)
            if np.random.rand() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""
                if new_value != current_value:
                    log_error(df, index, "4401")

            else:
                    
                # ERROR 4402 - Unnecessary Spaces (Leading, Trailing, Double)
                if np.random.rand() < 0.05:
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                    if new_value != current_value:
                        log_error(df, index, "4402")
                        current_value = new_value

                # ERROR 4403 - Invalid Characters (anything other than letters, BUT check for numbers is in contains digits)
                # anything other than letters contained in the GURS postal city field or anything other than numbers (since containning digits is a seperate error)
                if np.random.rand() < 0.04:
                    invalid_chars = ["◊", "�", "ß", "ø", "ç", "@", "#", "%", "&", "*", "~", "^", "!", "?", "_", "|", "/", "\\", "="]
                    eligible_chars = ["č", "š", "ž", "ć", "Č", "Š", "Ž", "Ć"]
                    new_value = ''.join(random.choice(invalid_chars) if char in eligible_chars else char for char in current_value)
                    if new_value != current_value:
                        log_error(df, index, "4403") 
                        current_value = new_value

                # ERROR 4404 - Formatting Issues
                if random.random() < 0.03:
                    if np.random.rand() < 0.5:
                        new_value = random.choice([current_value.upper(), current_value.lower(), current_value.capitalize()])
                    else:
                        # Randomly change the upper/lower case of letters
                        new_value = ''.join(random.choice([char.upper(), char.lower()]) for char in current_value)
                    if new_value != current_value:
                        log_error(df, index, "4404")
                        current_value = new_value

                # ERROR 4405 - Contains digits ()
                # copy the postal_code and paste it here 
                if np.random.rand() < 0.03:
                    new_value = f"{str(df.at[index, "POSTAL_CODE"])} {current_value}"
                    if new_value != current_value:
                        log_error(df, index, "4405")          
                        current_value = new_value
                
                # ERROR 4406 - Invalid Abbreviations
                # shorten the postal city to only leading two characters
                city_abbreviations = {
                    'Ljubljana': 'LJ',
                    'Celje': 'CE',
                    'Nova Gorica': 'GO',
                    'Krško': 'KK',
                    'Koper': 'KP',
                    'Kranj': 'KR',
                    'Maribor': 'MB',
                    'Murska Sobota': 'MS',
                    'Novo mesto': 'NM',
                    'Postojna': 'PO',
                    'Slovenj Gradec': 'SG'
                }
                if random.random() < 0.07:
                    if current_value in city_abbreviations:
                        new_value = city_abbreviations[current_value]
                        if new_value != current_value:
                            log_error(df, index, "4406")
                            current_value = new_value
                
                # ERROR 4407 - Duplicates
                if random.random() < 0.03:
                    new_value = f"{current_value} {current_value}"  # Duplicates error
                    if new_value != current_value:
                        log_error(df, index, "4407")
                        current_value = new_value

                # ERROR 4408 - Replace š, č, ž, ć with s, c, z, c
                if np.random.rand() < 0.06:
                    replacement_map = {"š": "s", "č": "c", "ž": "z", "ć": "c", "Š": "S", "Č": "C", "Ž": "Z", "Ć": "C"}
                    new_value = ''.join(replacement_map.get(char, char) for char in current_value)
                    if new_value != current_value:
                        log_error(df, index, "4408")
                        current_value = new_value

            df.at[index, "POSTAL_CITY"] = new_value  # Apply error to the column

    return df[["CUSTOMER_ID", "FIRST_NAME", "LAST_NAME", "EMAIL", "PHONE_NUMBER",
            "STREET", "HOUSE_NUMBER", "POSTAL_CODE", "POSTAL_CITY", "INTRODUCED_ERRORS"]]

# # ============================
# # **EXECUTION**
# # ============================

# Load the dataset (replace with your file path)
customer_data_path = "src/processed_data/customer_data.xlsx"
customer_df = pd.read_excel(customer_data_path, dtype=str)
# Ensure all columns are handled as strings
customer_df = customer_df.astype(str)

customer_df_w_errors = apply_errors(customer_df)

print("Errors introduced into the cusotmer dataset")

customer_df_w_errors.to_excel("src/processed_data/customer_data_with_errors.xlsx", index=False)
