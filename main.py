import pandas as pd
from utils.customer_data_generator import generate_synthetic_customer_data
from utils.chaos_engineering import apply_errors
from detection.detect_phone import detect_phone_errors
from detection.detect_email import detect_email_errors
from detection.detect_address import detect_address_errors
from detection.detect_names import detect_name_errors

########################################################################################
# 01. create customer datsaset

GURS_file_path = 'src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv'
# customer_df = generate_synthetic_customer_data(GURS_file_path, dataset_size=10000, seed=42)
customer_df = pd.read_excel("src/processed_data/customer_data.xlsx")
print("Synthetic customer dataset generated")
# customer_df.to_excel("src/processed_data/customer_data.xlsx", index=False)

########################################################################################
# 02. introduce errors into the dataset

# customer_df_w_errors = apply_errors(customer_df)
customer_df_w_errors = pd.read_excel("src/processed_data/customer_data_with_errors.xlsx")
print("Errors introduced into the cusotmer dataset")
# customer_df_w_errors.to_excel("src/processed_data/customer_data_with_errors.xlsx", index=False)

########################################################################################
# 03. Detect errors in the dataset

# Initialize the DETECTED_ERRORS column
customer_df_w_errors["DETECTED_ERRORS"] = ""

# Apply detect_name_errors to each row and append the results to the "DETECTED_ERRORS" column
customer_df_w_errors["DETECTED_ERRORS"] = customer_df_w_errors.apply(
    lambda row: (row["DETECTED_ERRORS"] + ',' if row["DETECTED_ERRORS"] else '') + detect_name_errors(row["FIRST_NAME"], row["LAST_NAME"]), axis=1)
# Apply detect_address to each row and append the results to the "DETECTED_ERRORS" column
customer_df_w_errors["DETECTED_ERRORS"] = customer_df_w_errors.apply(
    lambda row: detect_address_errors(row["STREET"], row["HOUSE_NUMBER"], row["POSTAL_CODE"], row["POSTAL_CITY"]), axis=1)
# Apply detect_phone_errors to each row and append the results to the "DETECTED_ERRORS" column
customer_df_w_errors["DETECTED_ERRORS"] = customer_df_w_errors.apply(
    lambda row: (row["DETECTED_ERRORS"] + ',' if row["DETECTED_ERRORS"] else '') + detect_phone_errors(row["PHONE_NUMBER"]), axis=1)
# Apply detect_email_errors to each row and append the results to the "DETECTED_ERRORS" column
customer_df_w_errors["DETECTED_ERRORS"] = customer_df_w_errors.apply(
    lambda row: (row["DETECTED_ERRORS"] + ',' if row["DETECTED_ERRORS"] else '') + detect_email_errors(row["EMAIL"]), axis=1)

print("Errors detected")

########################################################################################
# 04. Correct errors in the dataset



########################################################################################

########################################################################################
# 05. Evaluate the performance of the error detection and correction
########################################################################################
