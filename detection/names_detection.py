import re
import pandas as pd

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
    
    name_error_config = {
        '1101': {'message': 'NAME: Missing Data', 'detect': True, 'correct': False},
        '1102': {'message': 'NAME: Unnecessary Spaces', 'detect': True, 'correct': True},
        '1103': {'message': 'NAME: Invalid Characters', 'detect': True, 'correct': True},
        '1104': {'message': 'NAME: Formatting Issue', 'detect': True, 'correct': True},
        '1105': {'message': 'NAME: Duplicates', 'detect': True, 'correct': False},
        '1106': {'message': 'NAME: Two names in one field', 'detect': True, 'correct': False},

        '1201': {'message': 'SURNAME: Missing Data', 'detect': True, 'correct': False},
        '1202': {'message': 'SURNAME: Unnecessary Spaces', 'detect': True, 'correct': True},
        '1203': {'message': 'SURNAME: Invalid Characters', 'detect': True, 'correct': True},
        '1204': {'message': 'SURNAME: Formatting Issue', 'detect': True, 'correct': True},
        '1205': {'message': 'SURNAME: Duplicates', 'detect': True, 'correct': False},
    }


    # NAME errors detection
    
    # 1101 Check for missing data
    if pd.isna(name) or name is None or name.strip() == "" or name.strip() == "/" :
        name_errors.add('1101') 
    else:
        # 1102 Check for unnecessary spaces
        if name.startswith(' ') or name.endswith(' ') or "  " in name:
            name_errors.add('1102')
        # 1103 Check for invalid characters
        if not re.search(r'^[a-ž\s]+$', name, re.IGNORECASE):
            name_errors.add('1103')
        # 1104 Check for formatting issues
        if not name.istitle(): 
            name_errors.add('1104')
        # 1105 Check for duplicates
        names = name.split()
        counts = {}
        for name in names:
            if name not in counts:
                counts[name] = 0
            counts[name] += 1
        if any(count > 1 for count in counts.values()):
            name_errors.add('1105')
        # 1106 Check for two names in one field
        if len(names) > 1:
            name_errors.add('1106')
    
    # SURNAME errors detection
    # 1201 Missing Data
    if pd.isna(surname) or surname is None or surname.strip() == "" or surname.strip() == "/":
        surname_errors.add('1201')
    else:
        # 1202 Unnecessary Spaces
        if surname.startswith(' ') or surname.endswith(' ') or "  " in surname:
            surname_errors.add('1202')
        # 1204 Formatting Issue
        if not surname.istitle():
            surname_errors.add('1204')
        # 1205 Duplicates    
        surnames = surname.split()
        counts = {}
        for word in surnames:
            if word not in counts:
                counts[word] = 0
            counts[word] += 1
        if any(count > 1 for count in counts.values()):
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
