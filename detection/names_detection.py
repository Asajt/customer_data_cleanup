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
    rule_condition = name.strip() == "" or name.strip() == "x" or not re.search(r"[a-zA-Z0-9]", name)
    if should_detect('1101', error_config):
        if rule_condition:
            name_errors.add('1101') 
    
        else:
        
            # 1102 Check for unnecessary spaces
            rule_condition = (name.startswith(' ') or name.endswith(' ') or "  " in name)
            if should_detect('1102', error_config):
                if rule_condition:
                    name_errors.add('1102')
        
            # 1107 Initials present
            rule_condition = any(re.fullmatch(r"[A-ZČĆŠŽ]{1}\.?", word.strip()) for word in name.strip().split())
            if should_detect('1107', error_config):
                if rule_condition:
                    name_errors.add('1107')
        
            # 1103 Check for invalid characters
            skip_if_condition = not '1107' in name_errors
            rule_condition = (not re.search(r'^[a-zčćšžđ\s]+$', name, re.IGNORECASE))
            if should_detect('1103', error_config):
                if skip_if_condition:
                    if rule_condition:
                        name_errors.add('1103')

            # 1106 Check for two names in one field
            names = name.split()
            skip_if_condition = not '1107' in name_errors
            rule_condition = (len(names) > 1) and (re.search(r"\bin\b", name, re.IGNORECASE) or "," in name)
            if should_detect('1106', error_config):
                if skip_if_condition:
                    if rule_condition:
                        name_errors.add('1106')
        
            # 1105 Check for duplicates
            counts = {}
            for i in names:
                if i not in counts:
                    counts[i] = 0
                counts[i] += 1
            rule_condition = (any(count > 1 for count in counts.values()))
            if should_detect('1105', error_config):
                if rule_condition:
                    name_errors.add('1105')
                        
            # 1104 Check for formatting issues
            skip_if_condition = not (any (code in name_errors for code in ["1106", "1103"]))
            cleaned_name = re.sub(r"[^a-zA-ZčćšžđČĆŠŽĐ\s]", "", name.strip(), flags=re.IGNORECASE)
            rule_condition = (not cleaned_name.istitle())
            if should_detect('1104', error_config):
                if skip_if_condition:
                    if rule_condition:
                        name_errors.add('1104')
                        
    # SURNAME errors detection
    # 1201 Missing Data
    rule_condition = surname.strip() == "" or surname.strip() == "x" or not re.search(r"[a-zA-Z0-9]", surname)
    if should_detect('1201', error_config):
        if rule_condition:
            surname_errors.add('1201')
        
        else:
        
            # 1202 Unnecessary Spaces
            rule_condition = (surname.startswith(' ') or surname.endswith(' ') or "  " in surname)
            if should_detect('1202', error_config):
                if rule_condition:
                    surname_errors.add('1202')
        
            # 1203 Check for invalid characters
            rule_condition = (not re.search(r'^[a-zčćšžđ\s]+$', surname, re.IGNORECASE))
            if should_detect('1203', error_config):
                if rule_condition:
                    surname_errors.add('1203')
        
            # 1204 Formatting Issue
            cleaned_surname = re.sub(r"[^a-zA-ZčćšžđČĆŠŽĐ\s]", "", surname.strip(), flags=re.IGNORECASE)
            skip_if_condition = not '1203' in surname_errors
            rule_condition = (not cleaned_surname.istitle())
            if should_detect('1204', error_config):
                if rule_condition:
                    surname_errors.add('1204')
            
            # 1205 Duplicates    
            surnames = surname.split()
            counts = {}
            for i in surnames:
                if i not in counts:
                    counts[i] = 0
                counts[i] += 1
            rule_condition = (any(count > 1 for count in counts.values()))
            if should_detect('1205', error_config):
                if rule_condition:
                    surname_errors.add('1205')
                   
    # return ','.join(sorted(errors))
    # return {
    #     "name_detected_errors": sorted(name_errors),
    #     "surname_detected_errors": sorted(surname_errors)
    # }
    
    return sorted(name_errors), sorted(surname_errors)

if __name__ == "__main__":
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Apply the name error detection
    # errors_df = df.apply(
    #     lambda row: pd.Series(detect_name_errors(row["FIRST_NAME"], row["LAST_NAME"])),
    #     axis=1
    # )

    df[["name_detected_errors", "surname_detected_errors"]] = df.apply(
        lambda row: pd.Series(detect_name_errors(row["FIRST_NAME"], row["LAST_NAME"])),
        axis=1
    )

    # Convert lists to comma-separated strings just for saving
    df["name_detected_errors"] = df["name_detected_errors"].apply(lambda x: ", ".join(x))
    df["surname_detected_errors"] = df["surname_detected_errors"].apply(lambda x: ", ".join(x))

    # choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", "FIRST_NAME", "LAST_NAME", "name_detected_errors", "surname_detected_errors"
    ]
    df = df[columns_to_keep]
    
    # Save the result
    df.to_excel("src/processed_data/02_detected_name_errors.xlsx", index=False)
    print("Detection of name/surname errors completed and saved!")
