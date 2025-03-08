import pandas as pd
from utils.create_customer_dataset import load_data, save_data
from detection.detect_address import detect_address_errors
from correction.correct_address import correct_address_errors

# Load dataset
df = load_data("raw_data/customer_data_with_errors.xlsx")

# Address Error Detection
df_detected = detect_address_errors(df)

# Save detected errors
save_data(df_detected, "processed_data/customer_data_detected.xlsx")

# Address Error Correction
df_corrected = correct_address_errors(df_detected)

# Save corrected dataset
save_data(df_corrected, "processed_data/customer_data_corrected.xlsx")

print("Detection and Correction process completed successfully.")
