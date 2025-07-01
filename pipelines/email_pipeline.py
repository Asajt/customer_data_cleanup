import pandas as pd
import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
from detection.email_detection import detect_email_errors
from correction.email_correction import correct_email
from validation.email_validation import validate_email

def run_email_pipeline(df: pd.DataFrame, email_column) -> pd.DataFrame:
    """
    Run the email pipeline on the given DataFrame.
    This function performs the following steps:
    1. Validate emails using the validate_email function.
    2. Detect email errors using the detect_email_errors function.
    3. Correct detected errors using the correct_email_errors function.
    4. Re-validate emails after correction.
    5. Assign status to each email based on validation results.
    6. Return the updated DataFrame with additional columns for detected errors, corrections, and validation status.
    Args:
        df (pd.DataFrame): DataFrame containing customer data with columns "email".
        email_column (str): Name of the column containing emails.
    Returns:
        pd.DataFrame: Updated DataFrame with additional columns for detected errors, corrections, and validation status.
    """
    
    ################################################################################
    # Step 1: Validate emails
    df[f"{email_column}_VALID"] = df[email_column].apply(validate_email)

    print('EP: Email validation completed.')
    
    ################################################################################
    # Step 2: Detect errors
    df[f"{email_column}_DETECTED_ERRORS"] = df[email_column].apply(detect_email_errors)
    
    print('EP: Email detection completed.')
    
    ################################################################################
    # Create columns to check if there are errors
    df[f"{email_column}_HAS_ERRORS"] = df[f"{email_column}_DETECTED_ERRORS"].apply(lambda x: len(x) > 0)
    
    ################################################################################
    # Step 3: Correct if errors detected
    df[[f"{email_column}_CORRECTED", f"{email_column}_CORRECTED_ERRORS", f"{email_column}_UNCORRECTED_ERRORS"]] = df.apply(
        lambda row: pd.Series(correct_email(
            email=row[email_column],
            detected_email_errors=row[f"{email_column}_DETECTED_ERRORS"],
        )) if (len(row[f"{email_column}_DETECTED_ERRORS"]) > 0)
        else pd.Series([None, [], []])
        , axis=1
    )
    
    print('EP: Email correction completed.')
    
    ################################################################################
    # Check if the email was corrected
    df[f"{email_column}_WAS_CORRECTED"] = (df[f"{email_column}_CORRECTED"].notnull() | df[f"{email_column}_CORRECTED_ERRORS"].apply(lambda x: len(x) > 0))
    
    ################################################################################
    # Step 4: Re-validate for corrected emails
    df[f"{email_column}_VALID_AFTER_CORRECTION"] = df.apply(
        lambda row: validate_email(email=row[f"{email_column}_CORRECTED"]) 
        if row[f"{email_column}_WAS_CORRECTED"] else None,
        axis=1
    )
    
    print('EP: Email re-validation completed.')
    
    ################################################################################
    # Step 5: Assign status
    def status(row, column):
        detected_errors = row.get(f"{column}_DETECTED_ERRORS", [])

        # Check for MISSING DATA based on error code ending
        if any(str(error).endswith("01") for error in detected_errors):
            return "MISSING DATA"
        elif row.get(f"{column}_VALID"):
            return "VALID"
        elif not row.get(f"{column}_HAS_ERRORS", False):
            return "UNDETECTED ERRORS"
        elif row.get(f"{column}_UNCORRECTED_ERRORS"):
            return "UNCORRECTED ERRORS"
        elif row.get(f"{column}_VALID_AFTER_CORRECTION"):
            return "CORRECTED"
        else:
            return "INVALID AFTER CORRECTIONS"
    
    df[f"{email_column}_STATUS"] = df.apply(lambda row: status(row, email_column), axis=1)
    
    print('EP: Email status assignment completed.')
    
    return df

if __name__ == "__main__":
    # Load customer data
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Run the email pipeline
    df = run_email_pipeline(df, "EMAIL")

    # choose the columns to keep
    # columns_to_keep = [ ]
    # df = df[columns_to_keep]

    # Save updated file
    df.to_excel("src/processed_data/05_email.xlsx", index=False)
    print("Email pipeline completed successfully.")
