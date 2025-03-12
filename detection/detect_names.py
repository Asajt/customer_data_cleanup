import re
import pandas as pd

def detect_name_errors(name, surname):
    # Check for NaN values and convert them to empty strings
    name = "" if pd.isna(name) else str(name)
    surname = "" if pd.isna(surname) else str(surname)

    errors = set()
    
    error_messages = {
        '1101': 'NAME: Missing Data',
        '1102': 'NAME: Unnecessary Spaces',
        '1103': 'NAME: Invalid Characters',
        '1104': 'NAME: Formatting Issue',
        '1105': 'NAME: Duplicates',
        '1106': 'NAME: Two names in one field',
        
        '1201': 'SURNAME: Missing Data',
        '1202': 'SURNAME: Unnecessary Spaces',
        '1203': 'SURNAME: Invalid Characters',
        '1204': 'SURNAME: Formatting Issue',
        '1205': 'SURNAME: Duplicates'
    }

    # NAME errors detection
    
    # 1101 Check for missing data
    if pd.isna(name) or name is None or name.strip() == "" or name.strip() == "/" :
        errors.add('1101') 
    # 1102 Check for unnecessary spaces
    if name.startswith(' ') or name.endswith(' ') or "  " in name:
        errors.add('1102')
    # 1103 Check for invalid characters
    if not re.search(r'^[a-ž\s]+$', name, re.IGNORECASE):
        errors.add('1103')
    # 1104 Check for formatting issues
    if not name.istitle(): 
        errors.add('1104')
    # 1105 Check for duplicates
    names = name.split()
    counts = {}
    for name in names:
        if name not in counts:
            counts[name] = 0
        counts[name] += 1
    
    # SURNAME errors detection
    # 1201 Missing Data
    if pd.isna(surname) or surname is None or surname.strip() == "" or surname.strip() == "/":
        errors.add('1201')
    # 1202 Unnecessary Spaces
    if surname.startswith(' ') or surname.endswith(' ') or "  " in surname:
        errors.add('1202')
    # 1204 Formatting Issue
    if not name.istitle():
        errors.add('1204')
    # 1205 Duplicates    
    surnames = surname.split()
    counts = {}
    for word in surnames:
        if word not in counts:
            counts[word] = 0
        counts[word] += 1
    if any(count > 1 for count in counts.values()):
        errors.add('1205')
                
            
    return ','.join(sorted(errors))


# # TESTING

customer_data = "src/processed_data/customer_data_with_errors.xlsx"

df = pd.read_excel(customer_data)

# Apply the name error detection
df["DETECTED_ERRORS"] = df.apply(lambda row: detect_name_errors(row["FIRST_NAME"], row["LAST_NAME"]), axis=1)


print(df.head())
# # # Save the result to a new file
df.to_excel("src/processed_data/customer_data_with_detected_name_errors.xlsx", index=False)

print("Detection of name errors completed!")
