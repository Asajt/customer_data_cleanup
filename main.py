import pandas as pd
from pipelines.master_pipeline import run_full_quality_pipeline
from utils.customer_data_generator import generate_synthetic_customer_data
from utils.chaos_engineering import apply_errors

GURS_file_path = 'src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv'
dataset_size = 10000
seed = 42

def escape_excel_formulas(df):
    return df.apply(lambda col: col.map(lambda x: f"'{x}" if isinstance(x, str) and x.startswith("=") else x))

# generate synthetic customer data
df = generate_synthetic_customer_data(GURS_file_path, dataset_size, seed)

# introduce errors into the dataset
df = apply_errors(df, seed)

# Run the full quality pipeline
run_full_quality_pipeline(df, 
                              first_name_column="FIRST_NAME", 
                              last_name_column="LAST_NAME", 
                              street_column="STREET", 
                              street_number_column="HOUSE_NUMBER", 
                              postal_code_column="POSTAL_CODE", 
                              postal_city_column="POSTAL_CITY", 
                              email_column="EMAIL", 
                              phone_column="PHONE_NUMBER")

for col in df.columns:
        if "ERRORS" in col and df[col].dtype == "object":
            df[col] = df[col].apply(
                lambda x: ", ".join(sorted(x)) if isinstance(x, (set, list)) else x
            )

# Split the DataFrame into parts based on column prefixes
overview_df = df[["CUSTOMER_ID", "FIRST_NAME_STATUS", "LAST_NAME_STATUS", "STREET_STATUS",
                  "HOUSE_NUMBER_STATUS", "POSTAL_CODE_STATUS", "POSTAL_CITY_STATUS", 
                  "EMAIL_STATUS", "PHONE_NUMBER_STATUS", "OVERALL_STATUS"]]
names_df = df[["CUSTOMER_ID"] + [col for col in df.columns if col.startswith(("FIRST_NAME", "LAST_NAME"))]]
address_df = df[["CUSTOMER_ID", "FULL_ADDRESS", "FULL_ADDRESS_VALID", "FULL_ADDRESS_CORRECTED", "FULL_ADDRESS_VALID_AFTER_CORRECTION"] + [col for col in df.columns if col.startswith(("STREET", "HOUSE_NUMBER", "POSTAL_CODE", "POSTAL_CITY"))]]
email_df = df[["CUSTOMER_ID"] + [col for col in df.columns if col.startswith("EMAIL")]]
phone_df = df[["CUSTOMER_ID"] + [col for col in df.columns if col.startswith("PHONE_NUMBER")]]

# Escape Excel formulas in the DataFrames
overview_df = escape_excel_formulas(overview_df)
names_df    = escape_excel_formulas(names_df)
address_df  = escape_excel_formulas(address_df)
email_df    = escape_excel_formulas(email_df)
phone_df    = escape_excel_formulas(phone_df)

# create a excel writer object
with pd.ExcelWriter('src/processed_data/final_customer_data2.xlsx') as writer:
    overview_df.to_excel(writer, sheet_name="Overview", index=False)
    names_df.to_excel(  writer, sheet_name="Names", index=False)
    address_df.to_excel(writer, sheet_name="Address", index=False)
    email_df.to_excel(  writer, sheet_name="Email", index=False)
    phone_df.to_excel(  writer, sheet_name="Phone", index=False)

df.to_excel('src/processed_data/final_customer_data.xlsx', index=False)

print(f"Processed data saved")