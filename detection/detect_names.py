import re
import pandas as pd
import string

def detect_name_errors(name, surname):
    # Check for NaN values and convert them to empty strings
    name = "" if pd.isna(name) else str(name)
    surname = "" if pd.isna(surname) else str(surname)

    distinct_detected_errors = set()
    
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
    
    # Loop to decide how many times to process the address
    n = 3
    for i in range(n):
        errors = []  # List to store errors for this iteration
        
        # NAME errors detection
        
        # 1101 Check for missing data
        if pd.isna(name) or name is None or name.strip() == "" or name.strip() == "/" :
                errors.append('1101') 
                distinct_detected_errors.add('1101')
        # 1102 Check for unnecessary spaces
        if name.startswith(' ') or name.endswith(' ') or "  " in name:
            errors.append('1102')
            distinct_detected_errors.add('1102')
        # 1103 Check for invalid characters
        if not re.search(r'^[a-ž\s]+$', name, re.IGNORECASE):
            errors.append('1103')
            distinct_detected_errors.add('1103')
        # 1104 Check for formatting issues
        if not string.istitle(name): 
            errors.append('1104')
            distinct_detected_errors.add('1104')
        # 1105 Check for duplicates
        names = name.split()
        counts = {}
        for word in names:
            if word not in counts:
                counts[word] = 0
            counts[word] += 1
        if any(count > 1 for count in counts.values()):
            errors.append('1105')
            distinct_detected_errors.add('1105')
        # 1106 Check for two names in one field
        if len(names) > 1:
            if any(word.lower() == 'in' for word in names):
                errors.append('1106')
                distinct_detected_errors.add('1106')
        
        # SURNAME errors detection
        # 1201 Missing Data
        if pd.isna(surname) or surname is None or surname.strip() == "" or surname.strip() == "/":
            errors.append('1201')
            distinct_detected_errors.add('1201')
        # 1202 Unnecessary Spaces
        if surname.startswith(' ') or surname.endswith(' ') or "  " in surname:
            errors.append('1202')
            distinct_detected_errors.add('1202')
        # 1204 Formatting Issue
        if not string.istitle(surname):
            errors.append('1204')
            distinct_detected_errors.add('1204')
        # 1205 Duplicates    
        surnames = surname.split()
        counts = {}
        for word in surnames:
            if word not in counts:
                counts[word] = 0
            counts[word] += 1
        if any(count > 1 for count in counts.values()):
            errors.append('1205')
            
    return ','.join(sorted(distinct_detected_errors))