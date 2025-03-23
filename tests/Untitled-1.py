import pandas as pd

# Load the CSV file
# df = pd.read_csv("src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv")

# Find rows in ULICA_NAZIV which contain a dot (.)
# rows_with_dots = df[df['ULICA_NAZIV'].str.contains(r'\.', na=False, regex=True)]

# # Save the filtered data to an Excel file
# rows_with_dots.to_excel("src/processed_data/rows_with_dots.xlsx", index=False)



'''

import pandas as pd
import numpy as np
import re

current_value = "Ulica 15.maja"

#  # ERROR 4111 - Starts with Digit
# if re.search(r'\d', current_value):
#     match = re.search(r'\d', current_value) 
#     digit_index = match.start()  # Get its position
#     new_value = current_value[digit_index:]  # Keep only from the first digit onwards
#     print(f"Original value: {current_value}, New value: {new_value}")
    # desired output = 15.maja
    
    
# if re.search(r'\d+', current_value):
#     match = re.search(r'\d+', current_value) 
#     digit_index = match.start() + len(match.group())
#     new_value = current_value[:digit_index].strip() 
#     print(f"Original value: {current_value}, New value: {new_value}")
    # desired output = Ulica 15.maja
    
    

if re.search(r'\d+', current_value) and not re.search(r'\d+\.', current_value):
    if np.random.rand() < 0.5:
        match = re.search(r'\d', current_value) 
        digit_index = match.start()  # Get its position
        new_value = current_value[digit_index:]  # Keep only from the first digit onwards
        if new_value != current_value:
            print(f"Original value: {current_value}, New value: {new_value}")
            current_value = new_value
    elif np.random.rand() < 0.5:
        match = re.search(r'\d+', current_value) 
        digit_index = match.start() + len(match.group())
        new_value = current_value[:digit_index].strip() 
        if new_value != current_value:
            print(f"Original value: {current_value}, New value: {new_value}")
            current_value = new_value
            
'''

