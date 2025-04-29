import pandas as pd
import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
from detection.phone_detection import detect_phone_errors
from correction.phone_correction import correct_phone
from validation.phone_validation import validate_phone

def run_phone_pipeline(df: pd.DataFrame, phone_column) -> pd.DataFrame:
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
    # Step 1: Validate emails
    df[f"{phone_column}_VALID"] = df[phone_column].apply(validate_phone)

    print('df after validation:')
    print(df.head(10))
    print('#' * 50)
    ################################################################################
    
    ################################################################################
    df[f"{phone_column}_DETECTED_ERRORS"] = df[phone_column].apply(detect_phone_errors)
    
    print('df after detection:')
    print(df.head(10))
    df.to_excel("src/processed_data/04_pipeline_names_1.xlsx", index=False)
    print('#' * 50)
    
    ################################################################################
    # create columns to check if there are errors
    df[f"{phone_column}_HAS_ERRORS"] = df[f"{phone_column}_DETECTED_ERRORS"].apply(lambda x: len(x) > 0)
    
    print('df after adding detection bool:')
    print(df.head(10))
    df.to_excel("src/processed_data/04_pipeline_names_2.xlsx", index=False)
    print('#' * 50)
    
    ################################################################################
    # Step 3: Correct if errors detected
    '''
    define a row correction function which will be applied to each row if there are errors and 
    if there are no errors then it will return empty lists and empty errors for both name and surname
    '''

    # Apply correction function to each row
    df[[f"{phone_column}_CORRECTED", f"{phone_column}_CORRECTED_ERRORS", f"{phone_column}_UNCORRECTED_ERRORS"]] = df.apply(
        lambda row: pd.Series(correct_phone(
            phone=row[phone_column],
            detected_phone_errors=row[f"{phone_column}_DETECTED_ERRORS"],
        )) if (len(row[f"{phone_column}_DETECTED_ERRORS"]) > 0)
        else pd.Series([None, [], []])
        , axis=1
    )
    
    print('df after correction:')
    print(df.head(10))
    df.to_excel("src/processed_data/04_pipeline_names_3.xlsx", index=False)
    print('#' * 50)
    
    # create columns to check if there are errors
    df[f"{phone_column}_WAS_CORRECTED"] = df[f"{phone_column}_CORRECTED"].notnull()
    
    print('df after adding correction bool:')
    print(df.head(10))
    df.to_excel("src/processed_data/04_pipeline_names_4.xlsx", index=False)
    print('#' * 50)
    ################################################################################
    
    ################################################################################
    # Step 4: Re-validate for corrected emails
    df[f"{phone_column}_VALID_AFTER_CORRECTION"] = df.apply(
        lambda row: validate_phone(phone=row[f"{phone_column}_CORRECTED"]) 
        if row[f"{phone_column}_WAS_CORRECTED"] else None,
        axis=1
    )
    
    print('df after second validation:')
    print(df.head(10))
    df.to_excel("src/processed_data/04_pipeline_names_5.xlsx", index=False)
    print('#' * 50)
    ################################################################################
    
    ################################################################################
    # Step 5: Assign status
    def status(row, column):
        if row[f"{column}_VALID"]:
            return "VALID"
        if row[f"{column}_HAS_ERRORS"] and len(row[f"{column}_DETECTED_ERRORS"]) == len(row[f"{column}_CORRECTED_ERRORS"]):
            return "CORRECTED" if row[f"{column}_VALID_AFTER_CORRECTION"] else "PARTIALLY_CORRECTED"
        if row[f"{column}_HAS_ERRORS"] and len(row[f"{column}_CORRECTED_ERRORS"]) == 0:
            return "DETECTED"
        return "INVALID"
    
    df[f"{phone_column}_STATUS"] = df.apply(lambda row: status(row, phone_column), axis=1)
    
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
    df.to_excel("src/processed_data/05_email.xlsx", index=False)
    print("Phone pipeline completed successfully.")
