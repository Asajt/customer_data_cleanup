import pandas as pd
import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
from detection.names_detection import detect_name_errors
from correction.names_correction import correct_names
from validation.validate_names import validate_names

def run_name_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the name validation pipeline on the provided DataFrame.
    This function performs the following steps:
    1. Validate names using the validate_name function.
    2. Detect name and surname errors using the detect_name_errors function.
    3. Correct detected errors using the correct_name_errors function.
    4. Re-validate names after correction.
    5. Assign status to each name and surname based on validation results.
    6. Return the updated DataFrame with additional columns for detected errors, corrections, and validation status.
    
    Args:
        df (pd.DataFrame): DataFrame containing customer data with columns "name" and "surname".

    Returns:
        pd.DataFrame: Updated DataFrame with additional columns for detected errors, corrections, and validation status.
    """
    
    ################################################################################
    # Step 1: Validate names
    # df = validate_names(df, "FIRST_NAME", "LAST_NAME")
    print('df after validation:')
    print(df)
    print('#' * 50)
    ################################################################################
    
    ################################################################################
    # Step 2: Detect name + surname errors
    df = df.apply(
        lambda row: pd.Series(detect_name_errors(row["FIRST_NAME"], row["LAST_NAME"])),
        axis=1
    )
    print('df after validation:')
    print(df)
    print('#' * 50)
    ################################################################################
    
    ################################################################################
    # Step 3: Correct if errors detected
    '''
    define a row correction function which will be applied to each row if there are errors and 
    if there are no errors then it will return empty lists and empty errors for both name and surname
    '''
    df_new = df.apply(lambda row: pd.Series(correct_names( 
        first_name=row['FIRST_NAME'],
        last_name=row['LAST_NAME'],
        detected_first_name_errors=row["name_detected_errors"],
        detected_last_name_errors=row["surname_detected_errors"],
    )), axis=1)
    
    # Convert lists to comma-separated strings just for saving
    for col in df_new.columns:
        if "errors" in col:
            df_new[col] = df_new[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)    

    # Merge original and corrected data
    final_df = pd.concat([df, df_new], axis=1)
    print(list(final_df.columns))
    
    def correct(row):
        if row["has_name_errors"] or row["has_surname_errors"]:
            result = correct_name_errors(
                row["name"], row["surname"],
                row["name_detected_errors"], row["surname_detected_errors"]
            )
        else:
            result = {
                "name_corrected": [],
                "surname_corrected": [],
                "name_corrected_errors": [],
                "surname_corrected_errors": []
            }
        return pd.Series(result)

    # Apply the correction function to each row
    correction_df = df.apply(correct, axis=1)
    # concatenate the correction results with the original DataFrame
    df = pd.concat([df, correction_df], axis=1)
    df["was_name_corrected"] = df["name_corrected_errors"].apply(lambda x: len(x) > 0)
    df["was_surname_corrected"] = df["surname_corrected_errors"].apply(lambda x: len(x) > 0)
    ################################################################################
    
    ################################################################################
    # Step 4: Re-validate (only if fully corrected)
    '''
    define a row validation function which will be applied to each row if the length of the detected errors is 
    the same as the length of the corrected errors
    '''

    def validate_if_corrected(row):
        results = {"name_valid_after_correction": None, "surname_valid_after_correction": None}
        if len(row["name_detected_errors"]) == len(row["name_corrected_errors"]):
            results["name_valid_after_correction"] = validate_names(row["name_corrected"], row["surname_corrected"])["name_valid"]
        if len(row["surname_detected_errors"]) == len(row["surname_corrected_errors"]):
            results["surname_valid_after_correction"] = validate_names(row["name_corrected"], row["surname_corrected"])["surname_valid"]
        return pd.Series(results)

    # Apply the validation function to each row
    validation_df = df.apply(validate_if_corrected, axis=1)
    # concatenate the validation results with the original DataFrame
    df = pd.concat([df, validation_df], axis=1)
    ################################################################################
    
    ################################################################################
    # Step 5: Assign status
    def name_status(row):
        if row["name_valid"]:
            return "VALID"
        if row["has_name_errors"] and len(row["name_detected_errors"]) == len(row["name_corrected_errors"]):
            return "CORRECTED" if row["name_valid_after_correction"] else "PARTIALLY_CORRECTED"
        if row["has_name_errors"] and len(row["name_corrected_errors"]) == 0:
            return "DETECTED"
        return "INVALID"

    def surname_status(row):
        if row["surname_valid"]:
            return "VALID"
        if row["has_surname_errors"] and len(row["surname_detected_errors"]) == len(row["surname_corrected_errors"]):
            return "CORRECTED" if row["surname_valid_after_correction"] else "PARTIALLY_CORRECTED"
        if row["has_surname_errors"] and len(row["surname_corrected_errors"]) == 0:
            return "DETECTED"
        return "INVALID"
    
    df["NAME_STATUS"] = df.apply(name_status, axis=1)
    df["SURNAME_STATUS"] = df.apply(surname_status, axis=1)
    ################################################################################
    
    return df

if __name__ == "__main__":
    # Load customer data
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Run the name pipeline
    df = run_name_pipeline(df)

    # choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", "NAME", "SURNAME", "name_detected_errors", "surname_detected_errors",
        "has_name_errors", "has_surname_errors", "name_corrected", "surname_corrected",
        "name_corrected_errors", "surname_corrected_errors", "was_name_corrected",
        "was_surname_corrected", "name_valid_after_correction", "surname_valid_after_correction",
        "NAME_STATUS", "SURNAME_STATUS"
    ]
    df = df[columns_to_keep]

    # Save updated file
    df.to_excel("src/processed_data/01_validated_names.xlsx", index=False)
    print("Name validation complete.")
