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

# Save the processed data to an Excel file
output_file_path = 'src/processed_data/final_customer_data.xlsx'
df.to_excel(output_file_path, index=False)
print(f"Processed data saved to {output_file_path}")