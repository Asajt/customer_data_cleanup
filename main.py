import pandas as pd
#from utils.data_loader import load_data, save_data
from detection.detect_names import detect_name_errors
from detection.detect_address import detect_address_errors
from detection.detect_phone import detect_phone_errors
from detection.detect_email import detect_email_errors
from correction.correct_names import correct_name_errors
from correction.correct_address import correct_address_errors
from correction.correct_phone import correct_phone_errors
from correction.correct_email import correct_email_errors

# Load data
df = load_data("raw_data/dataset.csv")

# Detection
df = detect_name_errors(df)
df = detect_address_errors(df)
df = detect_phone_errors(df)
df = detect_email_errors(df)

# Correction
df = correct_name_errors(df)
df = correct_address_errors(df)
df = correct_phone_errors(df)
df = correct_email_errors(df)

# Save cleaned data
save_data(df, "cleaned_data/cleaned_dataset.csv")

print("Data Cleaning Complete! Cleaned dataset saved.")
