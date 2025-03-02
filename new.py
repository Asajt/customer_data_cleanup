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
            
            # ERROR 1101 - Duplicates
            if random.random() < 0.01:
                new_value = f"{current_value} {current_value}"  # Duplicates error
                log_error(df, index, "1101")
            
            # ERROR 1102 - Formatting Issues
            if random.random() < 0.03:
                new_value = random.choice([current_value.upper(), current_value.lower(), current_value.capitalize()])
                log_error(df, index, "1102")
            
            # ERROR 1103 - Invalid Characters (replace letters with numbers)
            if random.random() < 0.02:
                new_value = str(current_value).replace("a", "@").replace("o", "0").replace("e", "3").replace("i", "1")
                log_error(df, index, "1103")
            
            # ERROR 1104 - Missing Data
            if random.random() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""  # Missing Data error
                log_error(df, index, "1104")
            
            # ERROR 1105 - Two names in one field
            if random.random() < 0.01:
                second_name = random.choice(["Marija", "Janez", "Ana", "Marko"])
                new_value = f"{current_value} in {second_name}"  # Two names in one field error
                log_error(df, index, "1105")
            
            # ERROR 1106 - Unnecessary Spaces
            if random.random() < 0.03:
                if isinstance(current_value, str):
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                log_error(df, index, "1106")
            
            df.at[index, "FIRST_NAME"] = new_value  # Apply error to FIRST_NAME column


        # ============================
        # **LAST_NAME ERRORS**
        # ============================
        current_value = df.at[index, "LAST_NAME"]
        if np.random.rand() < 0.10:  # 10% chance for errors
            new_value = current_value  # Keep the original value until an error is applied
            
            # ERROR 1201 - Duplicates
            if random.random() < 0.01:
                new_value = f"{current_value} {current_value}"  # Duplicates error
                log_error(df, index, "1201")
            
            # ERROR 1202 - Invalid Characters
            if random.random() < 0.02:
                new_value = str(current_value).replace("a", "@").replace("o", "0").replace("e", "3").replace("i", "1")
                log_error(df, index, "1202")
            
            # ERROR 1203 - Missing Data
            if random.random() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""  # Missing data error
                log_error(df, index, "1203")
            
            # ERROR 1204 - Unnecessary Spaces
            if random.random() < 0.03:
                random_choice = random.choice(["leading", "trailing", "double"])
                if random_choice == "leading":
                    new_value = " " + current_value
                elif random_choice == "trailing":
                    new_value = current_value + " "
                elif random_choice == "double":
                    new_value = current_value.replace(" ", "  ", 1)
                
                log_error(df, index, "1204")
                
            df.at[index, "LAST_NAME"] = new_value  # Apply error to the column
            

        # ============================
        # **EMAIL ERRORS**
        # ============================
        current_value = df.at[index, "EMAIL"]
        invalid_domains = [
            "gmial.com", "gmaiul.com", "gmail.cm", "telemac.com", "hot*mail.com",
            "sioln.et", "sio.net", "sloveniamali.com", "email.si", "t-2.nt", "amis.nte"
        ]
        if np.random.rand() < 0.20:  # 20% chance for errors
            new_value = current_value  # Keep the original value until an error is applied
            
            # ERROR 2101 - Invalid Domain
            if random.random() < 0.02:
                local_part = current_value.split('@')[0]
                new_value = f"{local_part}@{random.choice(invalid_domains)}"
                log_error(df, index, "2101")
            
            # ERROR 2102 - Missing Data
            if np.random.rand() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""
                log_error(df, index, "2102")
            
            # ERROR 2103 - Invalid Characters & Encoding Issues
            if random.random() < 0.03:
                encoding_map = {"č": "c", "š": "s", "ž": "z"}
                modified_email = "".join(encoding_map.get(char, char) for char in current_value)
                new_value = modified_email.replace(".", ",").replace("@", "#")
                log_error(df, index, "2103")
            
            df.at[index, "EMAIL"] = new_value  # Apply error to EMAIL column


        # ============================
        # **PHONE_NUMBER ERRORS**
        # ============================
        current_value = df.at[index, "PHONE_NUMBER"]
        if np.random.rand() < 0.30:  # 30% chance for errors
            new_value = current_value  # Keep the original value until an error is applied
            
            # ERROR 3101 - Inconsistent Formatting
            if np.random.rand() < 0.10:
                new_value = random.choice([
                    current_value.replace("+386", "00386"),  
                    current_value.replace("+386", ""), 
                    current_value.replace("+386", "0"),
                    current_value.replace("+386", "+00386")
                ])
                log_error(df, index, "3101")
            
            # ERROR 3102 - Too Many Digits
            if random.random() < 0.01:
                new_value = current_value + str(random.randint(0, 9))  # Append a random digit
                log_error(df, index, "3102")
            
            # ERROR 3103 - Invalid Characters
            if np.random.rand() < 0.04:
                new_value = current_value.replace("0", "O").replace("1", "I")  # Replace digits with letters
                log_error(df, index, "3103")
            
            df.at[index, "PHONE_NUMBER"] = new_value  # Apply error to PHONE_NUMBER column


        # ============================
        # **STREET ERRORS**
        # ============================
        current_value = df.at[index, "STREET"]
        if np.random.rand() < 0.10:  # 10% chance for errors
            new_value = current_value  # Keep the original value until an error is applied
            
            # ERROR 4101 - Missing Data
            if random.random() < 0.05:
                new_value = np.nan if random.random() < 0.5 else ""  # Missing Data error
                log_error(df, index, "4101")
            
            # ERROR 4102 - Unnecessary Spaces
            if np.random.rand() < 0.05:
                if isinstance(current_value, str):
                    random_choice = random.choice(["leading", "trailing", "double"])  # Choose space type
                    if random_choice == "leading":
                        new_value = " " + current_value  # Add 1 leading space
                    elif random_choice == "trailing":
                        new_value = current_value + " "  # Add 1 trailing space
                    elif random_choice == "double":
                        new_value = current_value.replace(" ", "  ", 1)  # Replace first space with double space
                log_error(df, index, "4102")
            
            df.at[index, "STREET"] = new_value  # Apply error to STREET column


# ============================
# **EXECUTION**
# ============================

# Load the dataset (replace with your file path)
customer_data_path = "customer_data.xlsx"
customer_df = pd.read_excel(customer_data_path, dtype=str)

# Ensure all columns are handled as strings
customer_df = customer_df.astype(str)

# Add a column to track introduced errors
customer_df["introduced_errors"] = ""

# Apply errors
apply_errors(customer_df)

# Save the final dataset to Excel
customer_df.to_excel("customer_data_with_errors.xlsx", index=False, engine="openpyxl")
print("Corrupted dataset saved successfully.")
