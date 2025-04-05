import re
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.errors_utils import should_detect, load_error_config

error_config = load_error_config()

def detect_name_errors(name, surname):
    """Detects errors in names and surnames based on various criteria.

    This function checks for missing data, unnecessary spaces, invalid characters,
    formatting issues, duplicates, and the presence of multiple names in a single field.

    Args:
        name (str): The name to be checked
        surname (str): The surname to be checked.

    Returns:
        dict: A dictionary containing detected errors for both name and surname.
        The keys are:
            - "name_detected_errors": A list of error codes for the name.
            - "surname_detected_errors": A list of error codes for the surname.
    """
    # Check for NaN values and convert them to empty strings
    name = "" if pd.isna(name) else str(name)
    surname = "" if pd.isna(surname) else str(surname)

    name_errors = set()
    surname_errors = set()
    
    # NAME errors detection
    
    # 1101 Check for missing data
    rule_condition = (pd.isna(name) or name is None or name.strip() == "" or name.strip() == "/") 
    if should_detect('1101', error_config) and rule_condition:
        name_errors.add('1101') 
    
    else:
    
        # 1102 Check for unnecessary spaces
        rule_condition = (name.startswith(' ') or name.endswith(' ') or "  " in name)
        if should_detect('1102', error_config) and rule_condition:
            name_errors.add('1102')
    
        # 1103 Check for invalid characters
        rule_condition = (not re.search(r'^[a-ž\s]+$', name, re.IGNORECASE))
        if should_detect('1103', error_config) and rule_condition:
            name_errors.add('1103')
    
        # 1104 Check for formatting issues
        rule_condition = (not name.istitle())
        if should_detect('1104', error_config) and rule_condition:
            name_errors.add('1104')
    
        # 1105 Check for duplicates
        names = name.split()
        counts = {}
        for name in names:
            if name not in counts:
                counts[name] = 0
            counts[name] += 1
        rule_condition = (any(count > 1 for count in counts.values()))
        if should_detect('1105', error_config) and rule_condition:
            name_errors.add('1105')
    
        # 1106 Check for two names in one field
        rule_condition = (len(names) > 1)
        if should_detect('1106', error_config) and rule_condition:
            name_errors.add('1106')
    
    # SURNAME errors detection
    # 1201 Missing Data
    rule_condition = (pd.isna(surname) or surname is None or surname.strip() == "" or surname.strip() == "/")
    if should_detect('1201', error_config) and rule_condition:
        surname_errors.add('1201')
    
    else:
    
        # 1202 Unnecessary Spaces
        rule_condition = (surname.startswith(' ') or surname.endswith(' ') or "  " in surname)
        if should_detect('1202', error_config) and rule_condition:
            surname_errors.add('1202')
    
        # 1204 Formatting Issue
        rule_condition = (not surname.istitle())
        if should_detect('1204', error_config) and rule_condition:
            surname_errors.add('1204')
    
        # 1205 Duplicates    
        surnames = surname.split()
        counts = {}
        for word in surnames:
            if word not in counts:
                counts[word] = 0
            counts[word] += 1
        rule_condition = (any(count > 1 for count in counts.values()))
        if should_detect('1205', error_config) and rule_condition:
            surname_errors.add('1205')
                   
    # return ','.join(sorted(errors))
    return {
        "name_detected_errors": sorted(name_errors),
        "surname_detected_errors": sorted(surname_errors)
    }

if __name__ == "__main__":
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Apply the name error detection
    errors_df = df.apply(
        lambda row: pd.Series(detect_name_errors(row["FIRST_NAME"], row["LAST_NAME"])),
        axis=1
    )

    # Convert lists to comma-separated strings just for saving
    df["name_detected_errors"] = errors_df["name_detected_errors"].apply(lambda x: ", ".join(x))
    df["surname_detected_errors"] = errors_df["surname_detected_errors"].apply(lambda x: ", ".join(x))

    # choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", "FIRST_NAME", "LAST_NAME", "name_detected_errors", "surname_detected_errors"
    ]
    df = df[columns_to_keep]
    
    # Save the result
    df.to_excel("src/processed_data/02_detected_name_errors.xlsx", index=False)
    print("Detection of name/surname errors completed and saved!")
