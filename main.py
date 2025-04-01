import pandas as pd
from utils.customer_data_generator import generate_synthetic_customer_data
from utils.chaos_engineering import apply_errors
from detection.detect_phone import detect_phone_errors
from detection.detect_email import detect_email_errors
from detection.detect_address import detect_address_errors
from detection.detect_names import detect_name_errors

GURS_file_path = 'src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv'

########################################################################################
# 01. create customer datsaset
customer_df = generate_synthetic_customer_data(GURS_file_path, dataset_size=10000, seed=42)
########################################################################################

print(customer_df.head())

########################################################################################
# 02. introduce errors into the dataset
customer_df_w_errors = apply_errors(customer_df)
########################################################################################

print(customer_df_w_errors.head())

########################################################################################
# 03. Detect errors in the dataset
detect_name_errors(customer_df_w_errors)
detect_email_errors(customer_df_w_errors)
detect_address_errors(customer_df_w_errors)
detect_phone_errors(customer_df_w_errors)



########################################################################################

########################################################################################
# 04. Correct errors in the dataset
########################################################################################

########################################################################################
# 05. Evaluate the performance of the error detection and correction
########################################################################################
