import pandas as pd
from pipelines.master_pipeline import run_full_quality_pipeline
from utils.customer_data_generator import generate_synthetic_customer_data
from utils.chaos_engineering import apply_errors

GURS_file_path = 'src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv'
dataset_size = 10000
seed = 42

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
names_df = df[["CUSTOMER_ID", "INTRODUCED_ERRORS"] + [col for col in df.columns if col.startswith(("FIRST_NAME", "LAST_NAME"))]]
address_df = df[["CUSTOMER_ID", "INTRODUCED_ERRORS"] + [col for col in df.columns if col.startswith(("STREET", "HOUSE_NUMBER", "POSTAL_CODE", "POSTAL_CITY"))]]
email_df = df[["CUSTOMER_ID", "INTRODUCED_ERRORS"] + [col for col in df.columns if col.startswith("EMAIL")]]
phone_df = df[["CUSTOMER_ID", "INTRODUCED_ERRORS"] + [col for col in df.columns if col.startswith("PHONE_NUMBER")]]

# create a excel writer object
with pd.ExcelWriter('src/processed_data/final_customer_data2.xlsx') as writer:
    names_df.to_excel(  writer, sheet_name="Names", index=False)
    address_df.to_excel(writer, sheet_name="Address", index=False)
    email_df.to_excel(  writer, sheet_name="Email", index=False)
    phone_df.to_excel(  writer, sheet_name="Phone", index=False)

df.to_excel('src/processed_data/final_customer_data.xlsx', index=False)

print(f"Processed data saved")