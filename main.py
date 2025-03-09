import pandas as pd
from utils.customer_data_generator import generate_synthetic_customers
from utils.chaos_engineering import apply_errors
from detection.detect_address import detect_address_errors
from correction.correct_address import correct_address_errors
import pandas as pd
import numpy as np


GURS_file_path = 'src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv'
output_file_path = 'src/raw_data/customer_data.xlsx'

########################################################################################
# 01. create customer datsaset
customer_df = generate_synthetic_customers(file_path = GURS_file_path, dataset_size=5000, output_file_path=output_file_path, seed=42)
########################################################################################


########################################################################################
# 02. introduce errors into the dataset
#   Ensure all columns are handled as strings
customer_df = customer_df.astype(str)
#    Add a column to track introduced errors
customer_df["introduced_errors"] = ""
#   Apply errors
customer_df_w_errors = apply_errors(customer_df)
########################################################################################


# Save the final dataset
customer_df.to_excel("src/processed_data/customer_data_with_errors.xlsx", index=False)
print("Corrupted dataset saved successfully.")



# Address Error Detection
df_detected = detect_address_errors(df)

# Save detected errors
save_data(df_detected, "processed_data/customer_data_detected.xlsx")

# Address Error Correction
df_corrected = correct_address_errors(df_detected)

# Save corrected dataset
save_data(df_corrected, "processed_data/customer_data_corrected.xlsx")

print("Detection and Correction process completed successfully.")
