import pandas as pd
import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
from pipelines.names_pipeline import run_name_pipeline
from pipelines.email_pipeline import run_email_pipeline
from pipelines.address_pipeline import run_address_pipeline
from pipelines.phone_pipeline import run_phone_pipeline
from utils.customer_data_generator import generate_synthetic_customer_data
from utils.chaos_engineering import apply_errors

def run_preparation_pipeline(GURS_file_path, dataset_size, seed):
    # Create the synthetic customer data
    df = generate_synthetic_customer_data(GURS_file_path, dataset_size, seed)
    
    # introduce errors into the dataset
    df = apply_errors(df, seed)

    return df

def run_full_quality_pipeline(df, 
                              first_name_column, last_name_column, 
                              street_column, street_number_column, postal_code_column, postal_city_column, 
                              email_column, 
                              phone_column) -> pd.DataFrame:
    """
    Run the full quality pipeline on the provided DataFrame.
    This function performs the following steps:
    1. Run the name pipeline to validate, detect, and correct name errors.
    2. Run the email pipeline to validate and correct email addresses.
    3. Run the address pipeline to validate and correct addresses.  
    4. Run the phone pipeline to validate and correct phone numbers.
    5. Return the updated DataFrame with additional columns for detected errors, corrections, and validation status.
    Args:
        df (pd.DataFrame): DataFrame containing customer data with columns for names, emails, addresses, and phone numbers.
        first_name_column (str): Name of the column containing first names.
        last_name_column (str): Name of the column containing last names.
        street_column (str): Name of the column containing street names.
        street_number_column (str): Name of the column containing street numbers.
        postal_code_column (str): Name of the column containing postal codes.
        postal_city_column (str): Name of the column containing postal cities.
        email_column (str): Name of the column containing emails.
        phone_column (str): Name of the column containing phone numbers.
    Returns:
        pd.DataFrame: Updated DataFrame with additional columns for detected errors, corrections, and validation status.
    """
    df = run_name_pipeline(df, first_name_column, last_name_column)
    print('Name pipeline done')
    
    df = run_email_pipeline(df, email_column)
    print('Email pipeline done')
    
    df = run_address_pipeline(df, 
                              street_column, street_number_column, 
                              postal_code_column, postal_city_column)
    print('Address pipeline done')
    
    df = run_phone_pipeline(df, phone_column)
    print('Phone pipeline done')
    
    # Step 5: Assign overall status based on individual statuses
    def overall_status(row):
        statuses = [
            row[f"{first_name_column}_STATUS"],
            row[f"{last_name_column}_STATUS"],
            row[f"{street_column}_STATUS"],
            row[f"{street_number_column}_STATUS"],
            row[f"{postal_code_column}_STATUS"],
            row[f"{postal_city_column}_STATUS"],
            row[f"{email_column}_STATUS"],
            row[f"{phone_column}_STATUS"]
        ]
        
        if all(status == "VALID" for status in statuses):
            return "VALID"
        if any(status == "INVALID" for status in statuses):
            return "INVALID"
        if any(status == "CORRECTED" for status in statuses):
            return "CORRECTED"
        if any(status == "UNCORRECTED" for status in statuses):
            return "UNCORRECTED"
        return "PARTIALLY_VALID"
    
    df["OVERALL_STATUS"] = df.apply(overall_status, axis=1)
    
    print('Overall status assigned')
    
    return df

if __name__ == "__main__":
    
    path_to_gurs = 'src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv'
    dataset_size = 10000
    seed = 42
    
    df = run_preparation_pipeline(path_to_gurs, dataset_size, seed)
    
    # Example usage
    # customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    # df = pd.read_excel(customer_data)

    run_full_quality_pipeline(df, 
                              first_name_column="FIRST_NAME", 
                              last_name_column="LAST_NAME", 
                              street_column="STREET", 
                              street_number_column="HOUSE_NUMBER", 
                              postal_code_column="POSTAL_CODE", 
                              postal_city_column="POSTAL_CITY", 
                              email_column="EMAIL", 
                              phone_column="PHONE_NUMBER")
    
    # Convert lists and sets to strings before saving
    for col in df.columns:
        if "ERRORS" in col and df[col].dtype == "object":
            df[col] = df[col].apply(
                lambda x: ", ".join(sorted(x)) if isinstance(x, (set, list)) else x
            )
    
    df.to_excel("src/processed_data/final_customer_data.xlsx", index=False)
    print("Pipeline completed and saved to final_customer_data.xlsx")