import pandas as pd
import numpy as np
import random
import regex as re

# ============================
# **HELPER FUNCTION: LOG ERRORS**
# ============================
def log_error(df, row_id, error_id):
    """ Append error ID to introduced_errors column """
    if df.at[row_id, "introduced_errors"]:
        df.at[row_id, "introduced_errors"] += f" | {error_id}"
    else:
        df.at[row_id, "introduced_errors"] = str(error_id)


# ============================
# **APPLY ERRORS FUNCTION**
# ============================
def apply_errors(df):
    """
    Introduces errors into the dataset and tracks them in the 'introduced_errors' column.
    
    Parameters:
    df (pd.DataFrame): The dataset containing customer data.

    Returns:
    None (Modifies the dataframe in place and tracks applied errors)
    """
    for index in df.index:
        # ============================
        # **FIRST_NAME ERRORS**
        # ============================
        current_value = df.at[index, "FIRST_NAME"]
        if np.random.rand() < 0.15:
            new_value = current_value  # Keep the original value until an error is applied
            # ERROR 1101 - Missing Data
            if random.random() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""  # Missing Data error
                log_error(df, index, "1101")

                                
            # ERROR 1102 - Unnecessary Spaces
            if random.random() < 0.03:
                # Only apply the error if the current_value is a valid string (not NaN)
                if isinstance(current_value, str):
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                else:
                    new_value = current_value  # If it's NaN or not a string, keep it unchanged
                log_error(df, index, "1102")

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
                log_error(df, index, "1103")
            
            # ERROR 1104 - Formatting Issues
            if random.random() < 0.03:
                new_value = random.choice([current_value.upper(), current_value.lower(), current_value.capitalize()])
                log_error(df, index, "1104")
                            
            # ERROR 1105 - Duplicates
            if random.random() < 0.01:
                new_value = f"{current_value} {current_value}"  # Duplicates error
                log_error(df, index, "1105")
                
            # ERROR 1106 - Two names in one field
            if random.random() < 0.01:
                second_name = random.choice(["Marija", "Janez", "Ana", "Marko"])
                new_value = f"{current_value} in {second_name}"  # Two names in one field error
                log_error(df, index, "1106")
                
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
                log_error(df, index, "1201")

            # ERROR 1202 - Unnecessary Spaces
            if random.random() < 0.03:
                random_choice = random.choice(["leading", "trailing", "double"])
                if random_choice == "leading":
                    new_value = " " + current_value
                elif random_choice == "trailing":
                    new_value = current_value + " "  
                elif random_choice == "double":
                    new_value = current_value.replace(" ", "  ", 1)
                log_error(df, index, "1202")

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
                log_error(df, index, "1203")
                
            # ERROR 1204 - Formatting Issues
            if random.random() < 0.03:
                new_value = random.choice([current_value.upper(), current_value.lower(), current_value.capitalize()])
                log_error(df, index, "1204")                
                
            # ERROR 1205 - Duplicates
            if random.random() < 0.01:
                new_value = f"{current_value} {current_value}"  # Duplicates error
                log_error(df, index, "1205")        
                
                
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
                log_error(df, index, "2101")

            # ERROR 2102 - Unnecessary Spaces
            if random.random() < 0.03:
                random_choice = random.choice(["leading", "trailing", "double"])
                if random_choice == "leading":
                    new_value = " " + current_value
                elif random_choice == "trailing":
                    new_value = current_value + " "  
                elif random_choice == "double":
                    new_value = current_value.replace(" ", "  ", 1)
                log_error(df, index, "2102")

            # ERROR 2103 - Invalid Characters & Encoding Issues
            if random.random() < 0.03:
                encoding_map = {"č": "c", "š": "s", "ž": "z"}
                modified_email = "".join(encoding_map.get(char, char) for char in current_value)
                new_value = modified_email.replace(".", ",").replace("@", "#")
                log_error(df, index, "2103")
            
            # ERROR 2104 - Formatting Issue
            if np.random.rand() < 0.03:
                new_value = current_value.replace("@", "#").replace(".", "..")
                log_error(df, index, "2104")
                
            # ERROR 2105 - Duplicates
            if np.random.rand() < 0.02:
                new_value = f"{current_value}, {current_value}"
                log_error(df, index, "2105")                
                
            # ERROR 2106 - Two Emails
            if np.random.rand() < 0.01:
                extra_email = f"user{random.randint(1, 100)}@example.com"
                new_value = f"{current_value}, {extra_email}"    
                log_error(df, index, "2106")                
                
            # ERROR 2107 - Invalid Domain
            if random.random() < 0.02:
                local_part = current_value.split("@")[0]
                new_value = f"{local_part}@{random.choice(invalid_domains)}"
                log_error(df, index, "2107")                        
                
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
                log_error(df, index, "3101")

            # ERROR 3102 - Unnecessary Spaces
            if random.random() < 0.03:
                random_choice = random.choice(["leading", "trailing", "double"])
                if random_choice == "leading":
                    new_value = " " + current_value
                elif random_choice == "trailing":
                    new_value = current_value + " "  
                elif random_choice == "double":
                    new_value = current_value.replace(" ", "  ", 1)
                log_error(df, index, "3102")

            # ERROR 3103 - Invalid Characters
            if np.random.rand() < 0.04:
                new_value = current_value.replace("0", "O").replace("1", "I")  # Replace digits with letters
                log_error(df, index, "3103")

            # ERROR 3104 - Formatting Issues
            if np.random.rand() < 0.10:
                new_value = random.choice([
                    current_value.replace("+386", "00386"),  
                    current_value.replace("+386", ""), 
                    current_value.replace("+386", "0"),
                    current_value.replace("+386", "+00386")
                ])
                log_error(df, index, "3104")
                
            # ERROR 3105 - Too Many Digits
            if random.random() < 0.01:
                new_value = current_value + str(random.randint(0, 9))  # Append a random digit
                log_error(df, index, "3105")

            # ERROR 3106 - Too Few Digits
            if np.random.rand() < 0.03:
                num_digits_to_remove = random.randint(1, 3)  # Remove 1 to 3 digits randomly
                new_value = current_value[:-num_digits_to_remove]
                log_error(df, index, "3106")

           # ERROR 3107 - Two Phone Numbers
            if np.random.rand() < 0.02:
                extra_number = f"+38631{random.randint(100000, 999999)}"
                new_value = f"{current_value}, {extra_number}"
                log_error(df, index, "3107")

            # ERROR 3108 - Different country format
            if np.random.rand() < 0.05:
                alternative_country_codes = ["+385", "+49", "+33", "+44", "+30"]  # Croatia, Germany, France, UK, Greece
                new_country_code = random.choice(alternative_country_codes)
                new_value = current_value.replace("+386", new_country_code)
                log_error(df, index, "3108")
                
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
                log_error(df, index, "4101")
            
            # ERROR 4102 - Unnecessary Spaces
            if np.random.rand() < 0.05:
                # Only apply the error if the current_value is a valid string (not NaN)
                if isinstance(current_value, str):
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                else:
                    new_value = current_value  # If it's NaN or not a string, keep it unchanged
                log_error(df, index, "4102")

            # ERROR 4103 - Invalid Characters
            if np.random.rand() < 0.01:
                invalid_chars = ["◊", "�", "ß", "ø", "ç", "@", "#", "%", "&", "*", "~", "^", "!", "?", "_", "|", "/", "\\", "="]
                random_char = random.choice(invalid_chars)
                log_error(df, index, "4103")

           # ERROR 4104 - Contains House Number
            if np.random.rand() < 0.01:
                house_number_options = [
                    str(df.at[index, "HOUSE_NUMBER"]),  # Actual house number
                    str(random.randint(1, 999)),  # Random number
                    random.choice(["BŠ", "NH", "B$", "BS", "N.H.", "B.Š."]),  # Slovene indicator
                ]
                new_value = f"{current_value} {random.choice(house_number_options)}"
                log_error(df, index, "4104")

            # ERROR 4105 - Contains Variation of BŠ
            if np.random.rand() < 0.01:
                for term in ["BŠ", "NH", "B$", "BS", "N.H.", "B.Š."]:
                    new_value = current_value.replace(term, "")
                log_error(df, index, "4105")

            # ERROR 4106 - Invalid Abbreviations
            if np.random.rand() < 0.01:
                abbreviation_map = {"ul.": "ulica", "u.": "ulica", "ce.": "cesta", "c.": "cesta"}
                for abbr, full in abbreviation_map.items():
                    new_value = current_value.replace(abbr, full)
                log_error(df, index, "4106")

            # ERROR 4107 - No Space After Full Stop
            if np.random.rand() < 0.01:
                new_value = current_value.replace(". ", ".")
                log_error(df, index, "4107")

            # ERROR 4108 - Only Numbers
            if np.random.rand() < 0.01:
                new_value = "".join([str(random.randint(1, 9)) for _ in range(3)])
                log_error(df, index, "4108")

            # ERROR 4109 - Duplicates
            if np.random.rand() < 0.01:
                duplicate_type = random.choice(["full", "partial"])
                if duplicate_type == "full":
                    new_value = f"{current_value} {current_value}"
                else:
                    words = current_value.split()
                    if len(words) > 1:
                        new_value = " ".join(words + [words[-1]])
                log_error(df, index, "4109")

            # ERROR 4110 - Starts with Digit
            if np.random.rand() < 0.01:
                if current_value[0].isdigit():
                    new_value = f"Cesta {current_value}"
                log_error(df, index, "4110")

            # ERROR 4111 - More than 2 Commas
            if np.random.rand() < 0.01:
                new_value = current_value.replace(" ", ", ", 2)
                log_error(df, index, "4111")

            # ERROR 4112 - Cannot Contain Digit at the End
            if np.random.rand() < 0.01:
                if current_value[-1].isdigit():
                    new_value = current_value[:-1]
                log_error(df, index, "4112")
     
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
                log_error(df, index, "4201")                

            # ERROR 4202 - Unnecessary Spaces (Leading, Trailing, Double)
            if np.random.rand() < 0.05:
                # Only apply the error if the current_value is a valid string (not NaN)
                if isinstance(current_value, str):
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                    else:
                        new_value = current_value
                else:
                    new_value = current_value  # If it's NaN or not a string, keep it unchanged

                log_error(df, index, "4202")
                    
            # ERROR 4203 - Contains Variation of BŠ
            if np.random.rand() < 0.01:
                new_value = random.choice(["BŠ", "NH", f"BŠ {current_value}", f"NH {current_value}"])
                log_error(df, index, "4203")

            # ERROR 4204 - No House Number
            if np.random.rand() < 0.01:
                new_value = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                log_error(df, index, "4204")

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
                log_error(df, index, "4205")

            # ERROR 4206 - Leading 0
            if np.random.rand() < 0.01:
                if not current_value.startswith("0"):  # Avoid adding if already has leading zero
                    zeros_to_add = random.choice(["0", "00"])  # Randomly choose 1 or 2 zeros
                    new_value = zeros_to_add + current_value
                log_error(df, index, "4206")

            # ERROR 4207 - Spacing Between Components
            if np.random.rand() < 0.01:
                new_value = current_value.replace(" ", "").replace(".", "").replace("/", "")
                log_error(df, index, "4207")

            # ERROR 4208 - Contains Roman Numerals (1%)
            if np.random.rand() < 0.01:
                roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
                roman_choice = random.choice(roman_numerals)

                # Randomly decide whether to replace or prepend the house number
                if random.random() < 0.5:
                    new_value = f"{roman_choice} {current_value}"  # E.g., "IV 5"
                else:
                    new_value = roman_choice  # E.g., "IV"
                log_error(df, index, "4208")

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
                log_error(df, index, "4301")
                
            # ERROR 4302 - Unnecessary Spaces (Leading, Trailing, Double)
            if np.random.rand() < 0.05:
                # Only apply the error if the current_value is a valid string (not NaN)
                if isinstance(current_value, str):
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                else:
                    new_value = current_value  # If it's NaN or not a string, keep it unchanged
                log_error(df, index, "4302")
                
            # ERROR 4303 - Invalid Characters 
            if np.random.rand() < 0.01:
                new_value = current_value.replace("0", random.choice(["-", "/", "*", "X"]), 1)
                log_error(df, index, "4303")

            # ERROR 4304 - Less than 4 Digits (1%)
            if np.random.rand() < 0.01:
                new_value = current_value[:random.randint(1, 3)]  # Trim to <4 digits
                log_error(df, index, "4304")

            # ERROR 4305 - More than 4 Digits (1%)
            if np.random.rand() < 0.01:
                new_value = current_value + str(random.randint(0, 9))  # Extend with extra digit
                log_error(df, index, "4305")

           # ERROR 4306 - Contains Letters 
            if np.random.rand() < 0.01:
                postal_city = df.at[index, "POSTAL_CITY"] if "POSTAL_CITY" in df.columns else "Ljubljana"
                new_value = f"{postal_city} {current_value}" if random.random() < 0.5 else f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{current_value}"
                new_value = f"Ljubljana {current_value}"  # Fallback if city is missing
                log_error(df, index, "4306")                
            
            # ERROR 4307 - Invalid Value
            if np.random.rand() < 0.02:
                new_value = random.choice(["ABC", "0000", "99999"])
                log_error(df, index, "4307")
                
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
                log_error(df, index, "4401")

            # ERROR 4402 - Unnecessary Spaces (Leading, Trailing, Double)
            if np.random.rand() < 0.05:
                # Only apply the error if the current_value is a valid string (not NaN)
                if isinstance(current_value, str):
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                else:
                    new_value = current_value  # If it's NaN or not a string, keep it unchanged

            # ERROR 4403 - Invalid Characters (anything other than letters, BUT check for numbers is in contains digits)
            # anything other than letters contained in the GURS postal city field or anything other than numbers (since containning digits is a seperate error)
            if np.random.rand() < 0.01:
                special_chars = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/\\`~"
                random_char = random.choice(special_chars)
                position = random.randint(0, len(current_value))
                new_value = current_value[:position] + random_char + current_value[position:]
                log_error(df, index, "4403")            

            # ERROR 4404 - Contains digits ()
            # copy the postal_code and paste it here 
            if np.random.rand() < 0.01:
                new_value = f"{str(df.at[index, "POSTAL_CODE"])} {current_value}"
                log_error(df, index, "4404")            
            
            # ERROR 4405 - Invalid Abbreviations
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
            if random.random() < 0.10:
                if current_value in city_abbreviations:
                    new_value = city_abbreviations[current_value]
                    log_error(df, index, "4405")
            
            # ERROR 4406 - Duplicates
            if random.random() < 0.01:
                new_value = f"{current_value} {current_value}"  # Duplicates error
                log_error(df, index, "4406")

            df.at[index, "POSTAL_CITY"] = new_value  # Apply error to the column



# ============================
# **EXECUTION**
# ============================

# Load the dataset (replace with your file path)
customer_data_path = "src/processed_data/customer_data.xlsx"
customer_df = pd.read_excel(customer_data_path, dtype=str)
# Ensure all columns are handled as strings
customer_df = customer_df.astype(str)

# Add a column to track introduced errors
customer_df["introduced_errors"] = ""

# Apply errors
apply_errors(customer_df)

# Save the final dataset
customer_df.to_excel("src/processed_data/customer_data_with_errors.xlsx", index=False)
print("Corrupted dataset saved successfully.")
