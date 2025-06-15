import pandas as pd
import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
from detection.phone_detection import detect_phone_errors
from correction.phone_correction import correct_phone
from validation.phone_validation import validate_phone

def run_phone_pipeline(df: pd.DataFrame, phone_column: str) -> pd.DataFrame:
    """
    Run the phone pipeline on the given DataFrame.

    This function performs the following steps:
    1. Validate phones using the validate_phone function.
    2. Detect phone errors using the detect_phone_errors function.
    3. Correct detected errors using the correct_phone_errors function.
    4. Re-validate phones after correction.
    5. Assign status to each phone based on validation results.
    6. Return the updated DataFrame with additional columns for detected errors, corrections, and validation status.
    Args:
        df (pd.DataFrame): DataFrame containing customer data with columns "phone".
        phone_column (str): Name of the column containing phones.
    Returns:
        pd.DataFrame: Updated DataFrame with additional columns for detected errors, corrections, and validation status.
    """
    
    ################################################################################
    # Step 1: Validate phones
    df[f"{phone_column}_VALID"] = df[phone_column].apply(validate_phone)

    print('Phone validation completed.')
    
    ################################################################################
    # Step 2: Detect errors
    df[f"{phone_column}_DETECTED_ERRORS"] = df[phone_column].apply(detect_phone_errors)
    
    print('Phone detection completed.')
    
    ################################################################################
    # Create columns to check if there are errors
    df[f"{phone_column}_HAS_ERRORS"] = df[f"{phone_column}_DETECTED_ERRORS"].apply(lambda x: len(x) > 0)
    
    ################################################################################
    # Step 3: Correct if errors detected
    df[[f"{phone_column}_CORRECTED", f"{phone_column}_CORRECTED_ERRORS", f"{phone_column}_UNCORRECTED_ERRORS"]] = df.apply(
        lambda row: pd.Series(correct_phone(
            phone=row[phone_column],
            detected_phone_errors=row[f"{phone_column}_DETECTED_ERRORS"],
        )) if (len(row[f"{phone_column}_DETECTED_ERRORS"]) > 0)
        else pd.Series([None, [], []])
        , axis=1
    )
    
    print('Phone correction completed.')
    
    ################################################################################
    # Create columns to check which rows were corrected 
    df[f"{phone_column}_WAS_CORRECTED"] = df[f"{phone_column}_CORRECTED"].notnull()
    
    ################################################################################
    # Step 4: Re-validate for corrected phones
    df[f"{phone_column}_VALID_AFTER_CORRECTION"] = df.apply(
        lambda row: validate_phone(phone=row[f"{phone_column}_CORRECTED"]) 
        if row[f"{phone_column}_WAS_CORRECTED"] else None,
        axis=1
    )
    
    print('Phone re-validation completed.')

    ################################################################################    
    # Step 5: Assign status
    def status(row, column):
        if row[f"{column}_VALID"]:
            return "VALID"
        elif not row[f"{column}_HAS_ERRORS"]:
            return "UNDETECTED ERRORS"
        elif row[f"{column}_UNCORRECTED_ERRORS"]:
            return "UNCORRECTED ERRORS"
        elif row[f"{column}_VALID_AFTER_CORRECTION"]:
            return "CORRECTED"
        else:
            return "INVALID AFTER CORRECTIONS"
    
    df[f"{phone_column}_STATUS"] = df.apply(lambda row: status(row, phone_column), axis=1)
    
    print('Phone status assignment completed.')
    
    return df

if __name__ == "__main__":
    # Load customer data
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Run the phone pipeline
    df = run_phone_pipeline(df, "PHONE_NUMBER")

    # choose the columns to keep
    # columns_to_keep = [ ]
    # df = df[columns_to_keep]

    # Save updated file
    df.to_excel("src/processed_data/05_phone.xlsx", index=False)
    print("Phone pipeline completed successfully.")
