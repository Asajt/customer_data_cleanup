import pandas as pd
import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
from detection.address_detection import detect_address_errors
from correction.address_correction import correct_address
from validation.address_validation import validate_full_address

def load_gurs_data(path_to_gurs_RN_csv: str) -> pd.DataFrame:
    """
    Load GURS RN data from a CSV file and prepare it for validation.
    This function loads the GURS RN data, cleans the POSTNI_OKOLIS_NAZIV column,
    and creates a full address column for validation.

    Args:
        path_to_gurs_RN_csv (str): Path to the GURS RN CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the cleaned GURS RN data.
    """
    
    # Load and prepare GURS data
    print("Loading GURS data...")
    
    gurs_df = pd.read_csv(path_to_gurs_RN_csv, usecols = ['ULICA_NAZIV','HS_STEVILKA','HS_DODATEK','POSTNI_OKOLIS_SIFRA','POSTNI_OKOLIS_NAZIV'])
    
    # Remove dvojezična imena from POSTNI_OKOLIS_NAZIV
    gurs_df['POSTNI_OKOLIS_NAZIV'] = gurs_df['POSTNI_OKOLIS_NAZIV'].str.split('-').str[0].str.strip()
    print("POSTNI_OKOLIS_NAZIV cleaned.")
    
    gurs_df["GURS_FULL_ADDRESS"] = (
        gurs_df["ULICA_NAZIV"].str.strip() + " " +
        gurs_df["HS_STEVILKA"].fillna("").astype(str).str.strip() +
        gurs_df["HS_DODATEK"].fillna("").astype(str).str.strip() + ", " +
        gurs_df["POSTNI_OKOLIS_SIFRA"].fillna("").astype(str).str.strip() + " " +
        gurs_df["POSTNI_OKOLIS_NAZIV"].str.strip()
    )
    
    gurs_df = gurs_df[["GURS_FULL_ADDRESS"]]
    
    # Make a set of GURS_FULL_ADDRESS for faster lookup
    gurs_address_set = set(gurs_df['GURS_FULL_ADDRESS'].dropna().str.strip())
    
    print("GURS data loaded and prepared.")
    
    return gurs_address_set

def run_address_pipeline(df: pd.DataFrame, street_column, street_number_column, postal_code_column, postal_city_column) -> pd.DataFrame:
    """
    Run the address validation pipeline on the provided DataFrame.
    This function performs the following steps:
    1. Validate addresses using the validate_address function.
    2. Detect address errors using the detect_address_errors function.
    3. Correct detected errors using the correct_address_errors function.
    4. Re-validate addresses after correction.
    5. Assign status to each address component based on validation results.
    6. Return the updated DataFrame with additional columns for detected errors, corrections, and validation status.
    Args:
        df (pd.DataFrame): DataFrame containing customer data with columns "street", "street_number", "postal_code", and "postal_area".
        street_column (str): Name of the column containing street address.
        street_number_column (str): Name of the column containing street numbers.
        postal_code_column (str): Name of the column containing postal codes.
        postal_area_column (str): Name of the column containing postal areas.
    Returns:
        pd.DataFrame: Updated DataFrame with additional columns for detected errors, corrections, and validation status.
    """
    
    ################################################################################
    # Step 1: Validate address
    # Create FULL_ADDRESS
    df["FULL_ADDRESS"] = (
        df[street_column].str.strip() + " " +
        df[street_number_column].str.strip() + ", " +
        df[postal_code_column].str.strip() + " " +
        df[postal_city_column].str.strip())
    
    # Load GURS data ONCE
    gurs_address_set = load_gurs_data("src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv")
    
    # Apply validation
    df["FULL_ADDRESS_VALID"] = df["FULL_ADDRESS"].apply(lambda addr: validate_full_address(addr, gurs_address_set))

    print('Address validation completed.')
    
    ################################################################################
    # Step 2: Detect errors
    df[[f"{street_column}_DETECTED_ERRORS", 
        f"{street_number_column}_DETECTED_ERRORS", 
        f"{postal_code_column}_DETECTED_ERRORS", 
        f"{postal_city_column}_DETECTED_ERRORS"]] = df.apply(
            lambda row: pd.Series(detect_address_errors(row[street_column], row[street_number_column]
                                                        , row[postal_code_column], row[postal_city_column])),
        axis=1
    )
    
    print('Address detection completed.')
    
    ################################################################################
    # Create columns to check if there are errors
    df[f'{street_column}_HAS_ERRORS'] = df[f"{street_column}_DETECTED_ERRORS"].apply(lambda x: len(x) > 0)
    df[f'{street_number_column}_HAS_ERRORS'] = df[f"{street_number_column}_DETECTED_ERRORS"].apply(lambda x: len(x) > 0)
    df[f'{postal_code_column}_HAS_ERRORS'] = df[f"{postal_code_column}_DETECTED_ERRORS"].apply(lambda x: len(x) > 0)
    df[f'{postal_city_column}_HAS_ERRORS'] = df[f"{postal_city_column}_DETECTED_ERRORS"].apply(lambda x: len(x) > 0)
    
    ################################################################################
    # Step 3: Correct if errors detected
    df[[f"{street_column}_CORRECTED", f"{street_column}_CORRECTED_ERRORS", f"{street_column}_UNCORRECTED_ERRORS",
        f"{street_number_column}_CORRECTED", f"{street_number_column}_CORRECTED_ERRORS", f"{street_number_column}_UNCORRECTED_ERRORS",
        f"{postal_code_column}_CORRECTED", f"{postal_code_column}_CORRECTED_ERRORS", f"{postal_code_column}_UNCORRECTED_ERRORS",
        f"{postal_city_column}_CORRECTED", f"{postal_city_column}_CORRECTED_ERRORS", f"{postal_city_column}_UNCORRECTED_ERRORS"]] = df.apply(
        lambda row: pd.Series(correct_address(
            street=row[street_column],
            street_number=row[street_number_column],
            zipcode=row[postal_code_column],
            city=row[postal_city_column],
            detected_street_errors=row[f"{street_column}_DETECTED_ERRORS"],
            detected_street_number_errors=row[f"{street_number_column}_DETECTED_ERRORS"],
            detected_zipcode_errors=row[f"{postal_code_column}_DETECTED_ERRORS"],
            detected_city_errors=row[f"{postal_city_column}_DETECTED_ERRORS"]
        )) if (len(row[f"{street_column}_DETECTED_ERRORS"]) > 0 or len(row[f"{street_number_column}_DETECTED_ERRORS"]) > 0
                or len(row[f"{postal_code_column}_DETECTED_ERRORS"]) > 0 or len(row[f"{postal_city_column}_DETECTED_ERRORS"]) > 0)
        else pd.Series([None, [], [], None, [], [], None, [], [], None, [], []])
        , axis=1
    )
    
    print('Address correction completed.')
    
    ################################################################################
    # Create columns to check which rows were corrected
    df[f"{street_column}_WAS_CORRECTED"] = df[f"{street_column}_CORRECTED"].notnull()
    df[f"{street_number_column}_WAS_CORRECTED"] = df[f"{street_number_column}_CORRECTED"].notnull()
    df[f"{postal_code_column}_WAS_CORRECTED"] = df[f"{postal_code_column}_CORRECTED"].notnull()
    df[f"{postal_city_column}_WAS_CORRECTED"] = df[f"{postal_city_column}_CORRECTED"].notnull()
    
    ################################################################################
    # Step 4: Re-validate for corrected address
    # Create FULL_ADDRESS
    df["FULL_ADDRESS_CORRECTED"] = (
        df[f"{street_column}_CORRECTED"].str.strip() + " " +
        df[f"{street_number_column}_CORRECTED"].str.strip() + ", " +
        df[f"{postal_code_column}_CORRECTED"].str.strip() + " " +
        df[f"{postal_city_column}_CORRECTED"].str.strip())
    
    # Apply validation only if at least one of the components was corrected
    df["FULL_ADDRESS_VALID_AFTER_CORRECTION"] = df.apply(
        lambda row: validate_full_address(row["FULL_ADDRESS_CORRECTED"], gurs_address_set) 
        if  row[f"{street_column}_CORRECTED"] or 
            row[f"{street_number_column}_CORRECTED"] or 
            row[f"{postal_code_column}_CORRECTED"] or 
            row[f"{postal_city_column}_CORRECTED"]
        else None,
        axis=1
    )
    
    print('Address re-validation completed.')
    
    ################################################################################
    # Step 5: Assign status
    def status(row, column):
        if row[f"FULL_ADDRESS_VALID"]:
            return "VALID"
        if row[f"{column}_HAS_ERRORS"] and len(row[f"{column}_DETECTED_ERRORS"]) == len(row[f"{column}_CORRECTED_ERRORS"]):
            return "CORRECTED" if row[f"FULL_ADDRESS_VALID_AFTER_CORRECTION"] else "PARTIALLY_CORRECTED"
        if row[f"{column}_HAS_ERRORS"] and len(row[f"{column}_CORRECTED_ERRORS"]) == 0:
            return "DETECTED"
        return "INVALID"
    
    df[f"{street_column}_STATUS"] = df.apply(lambda row: status(row, street_column), axis=1)
    df[f"{street_number_column}_STATUS"] = df.apply(lambda row: status(row, street_number_column), axis=1)
    df[f"{postal_code_column}_STATUS"] = df.apply(lambda row: status(row, postal_code_column), axis=1)
    df[f"{postal_city_column}_STATUS"] = df.apply(lambda row: status(row, postal_city_column), axis=1)
    
    print('Address status assignment completed.')
    
    return df

if __name__ == "__main__":
    # Load customer data
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Run the address pipeline
    df = run_address_pipeline(df, "STREET", "HOUSE_NUMBER", "POSTAL_CODE", "POSTAL_CITY")

    # choose the columns to keep
    # columns_to_keep = [ ]
    # df = df[columns_to_keep]

    # Save updated file
    df.to_excel("src/processed_data/05_address.xlsx", index=False)
    print("Address pipeline completed successfully.")
