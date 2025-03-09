import pandas as pd
from utils.customer_data_generator import generate_synthetic_customer_data
from utils.chaos_engineering import apply_errors

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


########################################################################################

########################################################################################
# 04. Correct errors in the dataset
########################################################################################

########################################################################################
# 05. Evaluate the performance of the error detection and correction
########################################################################################
