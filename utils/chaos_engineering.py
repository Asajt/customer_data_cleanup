import pandas as pd
import numpy as np
import regex as re


# HELPER FUNCTION: LOG ERRORS (ordered, attribute-specific)
def log_error(df, row_id, error_id):
    """ Append error ID to INTRODUCED_ERRORS and attribute-specific error columns, keeping them sorted """
    # General error log
    current = df.at[row_id, "INTRODUCED_ERRORS"]
    if current:
        errors = [e.strip() for e in current.split(",") if e.strip()]
        if error_id not in errors:
            errors.append(str(error_id))
        errors = sorted(errors, key=lambda x: int(x))
        df.at[row_id, "INTRODUCED_ERRORS"] = ", ".join(errors)
    else:
        df.at[row_id, "INTRODUCED_ERRORS"] = str(error_id)

    # Attribute-specific log
    attr_map = {
        "11": "FIRST_NAME_INTRO_ERRORS",
        "12": "LAST_NAME_INTRO_ERRORS",
        "21": "EMAIL_INTRO_ERRORS",
        "31": "PHONE_NUMBER_INTRO_ERRORS",
        "41": "STREET_INTRO_ERRORS",
        "42": "HOUSE_NUMBER_INTRO_ERRORS",
        "43": "POSTAL_CODE_INTRO_ERRORS",
        "44": "POSTAL_CITY_INTRO_ERRORS"
    }
    # Use the first 1 or 2 digits to determine attribute
    attr_prefix = error_id[:2] if error_id[:2] in attr_map else error_id[:1]
    attr_col = attr_map.get(attr_prefix)
    if attr_col and attr_col in df.columns:
        current_attr = df.at[row_id, attr_col]
        if current_attr:
            errors_attr = [e.strip() for e in current_attr.split(",") if e.strip()]
            if error_id not in errors_attr:
                errors_attr.append(str(error_id))
            errors_attr = sorted(errors_attr, key=lambda x: int(x))
            df.at[row_id, attr_col] = ", ".join(errors_attr)
        else:
            df.at[row_id, attr_col] = str(error_id)

def apply_errors(df, seed):
    """
    Introduces errors into the dataset and tracks them in the 'INTRODUCED_ERRORS' column.
    
    Parameters:
    df (pd.DataFrame): The dataset containing customer data.

    Returns:
    None (Modifies the dataframe in place and tracks applied errors)
    """
    # Set random seed for reproducibility
    np.random.seed(seed)
    
    df = df.astype(str)
    
    # Initialize the error tracking column
    df['FIRST_NAME_INTRO_ERRORS'] = ""  
    df['LAST_NAME_INTRO_ERRORS'] = ""
    df['EMAIL_INTRO_ERRORS'] = ""
    df['PHONE_NUMBER_INTRO_ERRORS'] = ""
    df['STREET_INTRO_ERRORS'] = ""
    df['HOUSE_NUMBER_INTRO_ERRORS'] = ""
    df['POSTAL_CODE_INTRO_ERRORS'] = ""
    df['POSTAL_CITY_INTRO_ERRORS'] = ""
    df['INTRODUCED_ERRORS'] = ""  # General error tracking column    

    roman_numbers = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'
                , 'XI', 'XII', 'XIII', 'XIV','XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX'
                , 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII', 'XXVIII', 'XXIX', 'XXX'
                , 'XXXI'
                , 'XL']
    
    for index in df.index:
        # ============================
        # **FIRST_NAME ERRORS**
        # ============================
        current_value = df.at[index, "FIRST_NAME"]
        if np.random.rand() < 0.15:
            new_value = current_value  # Keep the original value until an error is applied
            # ERROR 1101 - Missing Data
            if np.random.rand() < 0.05:
                missing_variants = [None, "", "/", "//", "-", ".", "x"]
                new_value = np.random.choice(missing_variants)
                if new_value != current_value:
                    log_error(df, index, "1101")
            
            if "1101" not in df.at[index, "INTRODUCED_ERRORS"]:
                    # ERROR 1102 - Unnecessary Spaces
                    if np.random.rand() < 0.05:
                        random_choice = np.random.choice(["leading", "trailing", "double"])  # Choose space type
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
                    if np.random.rand() < 0.02:
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

                    # ERROR 1107 - Initials
                    if np.random.rand() < 0.01:
                        initials = ''.join([name[0].upper() + np.random.choice([".", ""]) for name in current_value.split()])
                        new_value = initials if len(current_value.split()) == 1 else current_value
                        if new_value != current_value:
                            log_error(df, index, "1107")
                            current_value = new_value
                            
                    # ERROR 1107 - Convert One Name to Initials
                    name_parts = current_value.split()
                    if len(name_parts) == 2:
                        if np.random.rand() < 0.3:
                            if np.random.rand() < 0.5:
                                new_value = f"{name_parts[0][0].upper()}." + f" {name_parts[1]}"
                            else:
                                # Convert the second name to an initial
                                new_value = f"{name_parts[0]} " + f"{name_parts[1][0].upper()}."
                    if new_value != current_value:
                        log_error(df, index, "1107")
                        current_value = new_value
                    
                    # ERROR 1105 - Duplicates
                    if np.random.rand() < 0.02:
                        duplicate_type = np.random.choice(["full", "partial"])
                        if duplicate_type == "full":
                            new_value = f"{current_value} {current_value}"
                        else:
                            words = current_value.split()
                            if len(words) > 1:
                                new_value = " ".join(words + [words[-1]])
                            else:
                                new_value = f"{current_value} {current_value}"
                        if new_value != current_value:
                            log_error(df, index, "1105")
                            current_value = new_value
                    
                    # ERROR 1104 - Formatting Issues
                    if np.random.rand() < 0.03:
                        if np.random.rand() < 0.5:
                            new_value = np.random.choice([current_value.upper(), current_value.lower(), current_value.capitalize()])
                        else:
                            # Randomly change the upper/lower case of letters
                            new_value = ''.join(np.random.choice([char.upper(), char.lower()]) for char in current_value)  # FIXED
                        if new_value != current_value:
                            log_error(df, index, "1104")
                            current_value = new_value
                        
                    # ERROR 1106 - Two names in one field
                    if np.random.rand() < 0.01:
                        second_name = np.random.choice(["Marija", "Janez", "Ana", "Marko"])
                        new_value = f"{current_value} in {second_name}"  # Two names in one field error
                        if new_value != current_value:
                            log_error(df, index, "1106")
                            current_value = new_value

                    # ERROR 1108 - Replace š, č, ž, ć with s, c, z, c
                    if np.random.rand() < 0.02:
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
        
        if np.random.rand() < 0.20:  
            new_value = current_value  # Keep the original value until an error is applied
            # ERROR 1201 - Missing Data
            if np.random.rand() < 0.05:
                missing_variants = [None, "", "/", "//", "-", ".", "x"]
                new_value = np.random.choice(missing_variants)
                if new_value != current_value:
                    log_error(df, index, "1201")
                
            if "1201" not in df.at[index, "INTRODUCED_ERRORS"]:

                    # ERROR 1202 - Unnecessary Spaces
                    if np.random.rand() < 0.04:
                        random_choice = np.random.choice(["leading", "trailing", "double"])
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
                    if np.random.rand() < 0.02:
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
                    
                    # ERROR 1205 - Duplicates
                    if np.random.rand() < 0.01:
                        duplicate_type = np.random.choice(["full", "partial"])
                        if duplicate_type == "full":
                            new_value = f"{current_value} {current_value}"
                        else:
                            words = current_value.split()
                            if len(words) > 1:
                                new_value = " ".join(words + [words[-1]])
                            else:
                                new_value = f"{current_value} {current_value}"
                        if new_value != current_value:
                            log_error(df, index, "1205")
                            current_value = new_value
                            
                    # ERROR 1204 - Formatting Issues
                    if np.random.rand() < 0.03:
                        if np.random.rand() < 0.5:
                            new_value = np.random.choice([current_value.upper(), current_value.lower(), current_value.capitalize()])
                        else:
                            # Randomly change the upper/lower case of letters
                            new_value = ''.join(np.random.choice([char.upper(), char.lower()]) for char in current_value)
                        if new_value != current_value:
                            log_error(df, index, "1204")
                            current_value = new_value
                        
                    # ERROR 1206 - Replace š, č, ž, ć with s, c, z, c
                    if np.random.rand() < 0.02:
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
        
        if np.random.rand() < 0.40:
            new_value = current_value  # Keep the original value until an error is applied
            # ERROR 2101 - Missing Data
            if np.random.rand() < 0.05:
                missing_variants = [None, "", "/", "//", "-", ".", "x"]
                new_value = np.random.choice(missing_variants)
                if new_value != current_value:
                    log_error(df, index, "2101")

            if "2101" not in df.at[index, "INTRODUCED_ERRORS"]:

                    # ERROR 2102 - Unnecessary Spaces
                    if np.random.rand() < 0.03:
                        random_choice = np.random.choice(["leading", "trailing", "double"])
                        if random_choice == "leading":
                            new_value = " " + current_value
                        elif random_choice == "trailing":
                            new_value = current_value + " "  
                        elif random_choice == "double":
                            new_value = current_value.replace(" ", "  ", 1)
                        if new_value != current_value:
                            log_error(df, index, "2102")
                            current_value = new_value

                    # ERROR 2103 - Invalid Characters
                    if np.random.rand() < 0.10:
                        if np.random.rand() < 0.3:
                            encoding_map = {"č": "/", "š": "∆", "ž": "?*"}
                            new_value = "".join(encoding_map.get(char, char) for char in current_value)
                        elif np.random.rand() < 0.5:
                            if np.random.rand() < 0.5:
                                new_value = current_value.replace(".", ",", 1) if np.random.rand() < 0.5 else current_value.replace(".", ",", 2) 
                            else:
                                new_value = current_value.replace("@", "#")
                        if new_value != current_value:
                            log_error(df, index, "2103")
                            current_value = new_value
                                    
                    # ERROR 2104 - Formatting Issue
                    if np.random.rand() < 0.03:
                        new_value = current_value  # Start with the original value
                        issue_type = np.random.choice(["missing_at", "double_dot", "missing_part"])
                        if issue_type == "missing_at":
                            new_value = current_value.replace("@", "")
                        elif issue_type == "double_dot":
                            if "." in current_value.split("@")[-1]:  # Ensure there's a domain part
                                new_value = current_value.replace(".", "..", 1) if np.random.rand() < 0.5 else current_value.replace(".", "", 1)
                        elif issue_type == "missing_part":
                            if np.random.rand() < 0.5:
                                new_value = "@" + current_value.split("@")[-1]  # Remove username
                            else:
                                new_value = current_value.split("@")[0] + "@"  # Remove domain
                        if new_value != current_value:
                            log_error(df, index, "2104")
                            current_value = new_value
                        
                    # ERROR 2105 - Possibly Two Emails
                    if np.random.rand() < 0.01:
                        usernames = np.random.choice(["tom", "majči", "novak.ana", "tclient", "admin"])
                        extra_email = f"{usernames}{np.random.randint(1, 100)}@gmail.com"
                        new_value = f"{current_value}, {extra_email}"    
                        if new_value != current_value:
                            log_error(df, index, "2105")
                            current_value = new_value
                        
                    # ERROR 2106 - Possibly Invalid Domain
                    if np.random.rand() < 0.05:
                        local_part = current_value.split("@")[0]
                        new_value = f"{local_part}@{np.random.choice(invalid_domains)}"
                        if new_value != current_value:
                            log_error(df, index, "2106")
                            current_value = new_value
                
            df.at[index, "EMAIL"] = new_value  # Apply error to the column


        # ============================
        # **PHONE_NUMBER ERRORS**
        # ============================
        current_value = df.at[index, "PHONE_NUMBER"]
        
        if np.random.rand() < 0.40: 
            new_value = current_value  # Keep the original value until an error is applied
            # ERROR 3101 - Missing Data
            if np.random.rand() < 0.07:
                missing_variants = [None, "", "/", "//", "-", ".", "x"]
                new_value = np.random.choice(missing_variants)
                if new_value != current_value:
                    log_error(df, index, "3101")
                
            if "3101" not in df.at[index, "INTRODUCED_ERRORS"]:

                    # ERROR 3102 - Unnecessary Spaces
                    if np.random.rand() < 0.03:
                        random_choice = np.random.choice(["leading", "trailing", "double"])
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
                        if np.random.rand() < 0.5:
                            new_value = current_value.replace("0", "O").replace("1", "I")  # Replace digits with letters
                        else:
                            for _ in range(np.random.randint(1, 2)):  # Replace 1 or 2 occurrences
                                new_value = re.sub("0", "O", new_value, count=1) if "0" in new_value and np.random.rand() < 0.5 else new_value
                                new_value = re.sub("1", "I", new_value, count=1) if "1" in new_value and np.random.rand() < 0.5 else new_value
                        if new_value != current_value:
                            log_error(df, index, "3103")
                            current_value = new_value

                    # ERROR 3104 - Formatting Issues
                    if np.random.rand() < 0.50:
                        if np.random.rand() < 0.5:
                            new_value = np.random.choice([
                                current_value.replace("00386", "+386"),  
                                current_value.replace("00386", ""), 
                                current_value.replace("00386", "0"),
                                current_value.replace("00386", "+00386")
                            ])
                        elif current_value.startswith("00386"):
                            new_value = current_value.replace("00386", "0")
                            pos1 = 3
                            pos2 = 6
                            separator = np.random.choice(["-", " ", "/"])
                            new_value = new_value[:pos1] + separator + new_value[pos1:pos2] + separator + new_value[pos2:]

                        if new_value != current_value:
                            log_error(df, index, "3104")
                            current_value = new_value

                    # ERROR 3105 - Too Many Digits
                    if np.random.rand() < 0.02:
                        new_value = current_value + str(np.random.randint(0, 9))  # Append a random digit
                        if new_value != current_value:
                            log_error(df, index, "3105")
                            current_value = new_value

                    # ERROR 3106 - Too Few Digits
                    if np.random.rand() < 0.03:
                        num_digits_to_remove = np.random.randint(1, 3)  # Remove 1 to 3 digits randomly
                        new_value = current_value[:-num_digits_to_remove]
                        if new_value != current_value:
                            log_error(df, index, "3106")
                            current_value = new_value

                    # ERROR 3107 - Two Phone Numbers
                    if np.random.rand() < 0.02:
                        extra_number = f"0038631{np.random.randint(100000, 999999)}"
                        new_value = f"{current_value}, {extra_number}"
                        if new_value != current_value:
                            log_error(df, index, "3107")
                            current_value = new_value

                    # ERROR 3108 - Different country format
                    if np.random.rand() < 0.03:
                        alternative_country_codes = ["+385", "+49", "+33", "+44", "+30", "00385", "0049", "0033", "0044", "0030"]  # Croatia, Germany, France, UK, Greece
                        new_country_code = np.random.choice(alternative_country_codes)
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
        if np.random.rand() < 0.20:
            new_value = current_value  # Keep the original value until an error is applied
            # ERROR 4101 - Missing Data
            if np.random.rand() < 0.05:
                missing_variants = [None, "", "/", "//", "-", ".", "x"]
                new_value = np.random.choice(missing_variants)
                if new_value != current_value:
                    log_error(df, index, "4101")

            if "4101" not in df.at[index, "INTRODUCED_ERRORS"]:
                        
                    # ERROR 4102 - Unnecessary Spaces
                    if np.random.rand() < 0.05:
                        random_choice = np.random.choice(["leading", "trailing", "double"])  # Choose space type
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
                        new_value = ''.join(np.random.choice(invalid_chars) if char in eligible_chars else char for char in current_value)
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
                    
                    # ERROR 4110 - Duplicates
                    if "4102" not in df.at[index, "INTRODUCED_ERRORS"]:
                        if np.random.rand() < 0.01:
                            duplicate_type = np.random.choice(["full", "partial"])
                            if duplicate_type == "full":
                                new_value = f"{current_value} {current_value}"
                            else:
                                words = current_value.split()
                                if len(words) > 1:
                                    new_value = " ".join(words + [words[-1]])
                                else:
                                    new_value = f"{current_value} {current_value}"
                            if new_value != current_value:
                                log_error(df, index, "4110")
                                current_value = new_value
                    
                    # ERROR 4104 - Formatting Issues
                    if np.random.rand() < 0.03:
                        if np.random.rand() < 0.5:
                            new_value = np.random.choice([current_value.upper(), current_value.lower(), current_value.capitalize()])
                        else:
                            # Randomly change the upper/lower case of letters
                            new_value = ''.join(np.random.choice([char.upper(), char.lower()]) for char in current_value)
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
                    if np.random.rand() < 0.2:
                        house_number_options = [
                            str(df.at[index, "HOUSE_NUMBER"]),  # Actual house number
                            str(np.random.randint(1, 999))]
                        new_value = f"{current_value} {np.random.choice(house_number_options)}"
                        if new_value != current_value:
                            log_error(df, index, "4105")
                            current_value = new_value
                        # Randomly decide whether to wipe out the actual HOUSE_NUMBER
                        if np.random.rand() < 0.5:  # 50% chance to also wipe out the actual HOUSE_NUMBER
                            df.at[index, "HOUSE_NUMBER"] = ""
                            log_error(df, index, "4201")  # Log the error for HOUSE_NUMBER as well

                    # ERROR 4106 - Contains Variation of BŠ
                    if np.random.rand() < 0.1:
                        terms = ("BŠ", "NH", "B$", "BS", "N.H.", "B.Š.")
                        new_value = current_value + f" {np.random.choice(terms)}"
                        if new_value != current_value:
                            log_error(df, index, "4106")
                            current_value = new_value

                    # ERROR 4107 - Invalid Abbreviations
                    if np.random.rand() < 0.3:
                        abbreviation_map = {
                            "ulica": ["ul.", "u."],
                            "cesta": ["c.", "ce."]}

                        for full, abbrs in abbreviation_map.items():
                            if full in current_value:  # If 'ulica' or 'cesta' exists
                                chosen_abbr = np.random.choice(abbrs)  # Randomly select an abbreviation
                                new_value = current_value.replace(full, chosen_abbr, 1)  # Replace first occurrence
                        if new_value != current_value:
                            log_error(df, index, "4107")
                            current_value = new_value

                    # ERROR 4109 - Only Numbers
                    if "4102" not in df.at[index, "INTRODUCED_ERRORS"]:
                        if np.random.rand() < 0.04:
                                new_value = "".join([str(np.random.randint(1, 9)) for _ in range(3)])
                                if new_value != current_value:
                                    log_error(df, index, "4109")
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
        if np.random.rand() < 0.20:
            new_value = current_value  # Keep the original value until an error is applied

            # ERROR 4201 - Missing Data
            if np.random.rand() < 0.05:
                missing_variants = [None, "", "/", "//", "-", ".", "x"]
                new_value = np.random.choice(missing_variants)
                if new_value != current_value:
                    log_error(df, index, "4201") 

            if "4201" not in df.at[index, "INTRODUCED_ERRORS"]:

                    # ERROR 4202 - Unnecessary Spaces (Leading, Trailing, Double)
                    if np.random.rand() < 0.05:
                        random_choice = np.random.choice(["leading", "trailing", "double"])  # Choose space type
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
                            
                    # ERROR 4203 - Contains Variation of BŠ & ERROR 4213 Contains BŠ as well as house number
                    if "4202" not in df.at[index, "INTRODUCED_ERRORS"]:
                        if np.random.rand() < 0.08:
                            new_value = np.random.choice(["BŠ", "NH", f"BŠ {current_value}", f"NH {current_value}"])
                            if new_value != current_value:
                                log_error(df, index, "4203")
                                current_value = new_value

                    # ERROR 4204 - No House Number
                    if "4202" not in df.at[index, "INTRODUCED_ERRORS"]:
                        if np.random.rand() < 0.04:
                            new_value = np.random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
                            if new_value != current_value:
                                log_error(df, index, "4204")
                                current_value = new_value

                    # ERROR 4205 - Invalid Combination
                    if "4202" not in df.at[index, "INTRODUCED_ERRORS"]:
                        if np.random.rand() < 0.20:
                            # Identify number and letter parts using regex
                            match = re.match(r"(\d+)([A-Za-z]?)", current_value)  # Extract number and optional letter
                            if match:
                                num_part, letter_part = match.groups()
                                if letter_part:  # If there is a letter, introduce a random separator
                                    separator = np.random.choice([" ", "-", "/"])
                                    new_value = f"{num_part}{separator}{letter_part}"
                                else:  # If no letter part, introduce one and add a separator
                                    new_value = f"{num_part}{np.random.choice(['A', 'B'])}"
                            if new_value != current_value:
                                log_error(df, index, "4205")
                                current_value = new_value

                    # ERROR 4206 - Leading 0
                    if np.random.rand() < 0.05:
                        if not current_value.startswith("0"):  # Avoid adding if already has leading zero
                            zeros_to_add = np.random.choice(["0", "00"])  # Randomly choose 1 or 2 zeros
                            new_value = zeros_to_add + current_value
                        if new_value != current_value:
                            log_error(df, index, "4206")
                            current_value = new_value

                    # ERROR 4207 - Spacing Between Components
                    if "4202" not in df.at[index, "INTRODUCED_ERRORS"]:
                        if np.random.rand() < 0.20:
                            new_value = current_value.replace(" ", "").replace(".", "").replace("/", "")
                            if new_value != current_value:
                                log_error(df, index, "4207")
                                current_value = new_value

                    # ERROR 4208 - Contains Roman Numerals (1%)
                    roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
                    if any(roman in str(df.at[index, "STREET"]) for roman in roman_numerals):
                        if np.random.rand() < 0.4:
                            roman_choice = np.random.choice(roman_numerals)

                            if np.random.rand() < 0.5:
                                new_value = f"{roman_choice} {current_value}"
                            else:
                                new_value = roman_choice

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
                        new_value = current_value + f" {np.random.randint(1, 99)}"
                        if new_value != current_value:
                            log_error(df, index, "4210")
                            current_value = new_value

                    # ERROR 4211 - Does not start with digit
                    if np.random.rand() < 0.01:
                        prefixes = ["St.", "HS", "HŠ", "A", "B", "H", "št.", "Stanovanje", "st."]
                        new_value = np.random.choice(prefixes) + " " + current_value
                        if new_value != current_value:
                            log_error(df, index, "4211")
                            current_value = new_value

                    # ERROR 4212 - More than 4 digits
                    if np.random.rand() < 0.01 and current_value.isdigit() and 2 <= len(current_value) <= 3:
                        new_value = current_value + str(np.random.randint(10, 99)) 
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
            
            # ERROR 4301 - Missing Data
            if np.random.rand() < 0.05:
                missing_variants = [None, "", "/", "//", "-", ".", "x"]
                new_value = np.random.choice(missing_variants)
                if new_value != current_value:
                    log_error(df, index, "4301")

            if "4301" not in df.at[index, "INTRODUCED_ERRORS"]:
                        
                    # ERROR 4302 - Unnecessary Spaces (Leading, Trailing, Double)
                    if np.random.rand() < 0.05:
                        random_choice = np.random.choice(["leading", "trailing", "double"])  # Choose space type
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
                        new_value = current_value.replace("0", np.random.choice(["-", "/", "*", "X"]), 1)
                        if new_value != current_value:
                            log_error(df, index, "4303")
                            current_value = new_value

                    # ERROR 4304 - Less than 4 Digits (1%)
                    if np.random.rand() < 0.01:
                        new_value = current_value[:np.random.randint(1, 3)]  # Trim to <4 digits
                        if new_value != current_value:
                            log_error(df, index, "4304")
                            current_value = new_value

                    # ERROR 4305 - More than 4 Digits (1%)
                    if np.random.rand() < 0.01:
                        new_value = current_value + str(np.random.randint(0, 9))  # Extend with extra digit
                        if new_value != current_value:
                            log_error(df, index, "4305")
                            current_value = new_value

                    # ERROR 4306 - Contains Letters 
                    if np.random.rand() < 0.01:
                        postal_city = df.at[index, "POSTAL_CITY"] if "POSTAL_CITY" in df.columns else "Ljubljana"
                        if np.random.rand() < 0.9:
                            new_value = f"{current_value} {postal_city}"
                        elif np.random.rand() < 0.2:
                            new_value = f"{np.random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))}{current_value}"
                        # Fallback if postal_city is missing or empty
                        elif np.random.rand() < 0.3:
                            new_value = f"Ljubljana {current_value}"
                        if new_value != current_value:
                            log_error(df, index, "4306")
                            current_value = new_value

                    # ERROR 4307 - Invalid Value
                    if np.random.rand() < 0.02:
                        new_value = np.random.choice(["ABC", "0000", "99999"])
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
            # ERROR 4401 - Missing Data
            if np.random.rand() < 0.05:
                missing_variants = [None, "", "/", "//", "-", ".", "x"]
                new_value = np.random.choice(missing_variants)
                if new_value != current_value:
                    log_error(df, index, "4401")

            if "4401" not in df.at[index, "INTRODUCED_ERRORS"]:
                        
                    # ERROR 4402 - Unnecessary Spaces (Leading, Trailing, Double)
                    if np.random.rand() < 0.05:
                        random_choice = np.random.choice(["leading", "trailing", "double"])  # Choose space type
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
                        new_value = ''.join(np.random.choice(invalid_chars) if char in eligible_chars else char for char in current_value)
                        if new_value != current_value:
                            log_error(df, index, "4403") 
                            current_value = new_value

                    # ERROR 4407 - Duplicates
                    if np.random.rand() < 0.02:
                        duplicate_type = np.random.choice(["full", "partial"])
                        new_value = current_value 
                        if duplicate_type == "full":
                            new_value = f"{current_value} {current_value}"
                        else:
                            words = current_value.split()
                            if len(words) > 1:
                                new_value = " ".join(words + [words[-1]])
                            else:
                                new_value = f"{current_value} {current_value}"
                        if new_value != current_value:
                            log_error(df, index, "4407")
                            current_value = new_value

                    # ERROR 4404 - Formatting Issues
                    if np.random.rand() < 0.03:
                        if np.random.rand() < 0.5:
                            new_value = np.random.choice([current_value.upper(), current_value.lower(), current_value.capitalize()])
                        else:
                            # Randomly change the upper/lower case of letters
                            new_value = ''.join(np.random.choice([char.upper(), char.lower()]) for char in current_value)
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
                    if np.random.rand() < 0.07:  # 7% chance to apply
                        if current_value in city_abbreviations:
                            abbr = city_abbreviations[current_value]
                            use_dot = np.random.rand() < 0.5  # 50% chance to add a dot
                            new_value = f"{abbr}." if use_dot else abbr
                            if new_value != current_value:
                                log_error(df, index, "4406")
                                current_value = new_value

                    # ERROR 4408 - Replace š, č, ž, ć with s, c, z, c
                    if np.random.rand() < 0.06:
                        replacement_map = {"š": "s", "č": "c", "ž": "z", "ć": "c", "Š": "S", "Č": "C", "Ž": "Z", "Ć": "C"}
                        new_value = ''.join(replacement_map.get(char, char) for char in current_value)
                        if new_value != current_value:
                            log_error(df, index, "4408")
                            current_value = new_value

            df.at[index, "POSTAL_CITY"] = new_value  # Apply error to the column

    return df[["CUSTOMER_ID", 
               "FIRST_NAME", "FIRST_NAME_INTRO_ERRORS", 
               "LAST_NAME", "LAST_NAME_INTRO_ERRORS", 
               "EMAIL", "EMAIL_INTRO_ERRORS",
               "PHONE_NUMBER", "PHONE_NUMBER_INTRO_ERRORS",
               "STREET", "STREET_INTRO_ERRORS",
               "HOUSE_NUMBER", "HOUSE_NUMBER_INTRO_ERRORS",
               "POSTAL_CODE",  "POSTAL_CODE_INTRO_ERRORS", 
               "POSTAL_CITY", "POSTAL_CITY_INTRO_ERRORS",
               "INTRODUCED_ERRORS"]]

if __name__ == "__main__":
    # Load the dataset (replace with your file path)
    customer_data_path = "src/processed_data/customer_data.xlsx"
    customer_df = pd.read_excel(customer_data_path, dtype=str)
    # Ensure all columns are handled as strings
    customer_df = customer_df.astype(str)

    customer_df_w_errors = apply_errors(customer_df, seed=42)

    print("Errors introduced into the cusotmer dataset")
    customer_df_w_errors.to_excel("src/processed_data/customer_data_with_errors.xlsx", index=False)
    print("Customer data with errors saved to 'customer_data_with_errors.xlsx'")   