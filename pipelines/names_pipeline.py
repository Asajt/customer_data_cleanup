import pandas as pd
import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
from detection.names_detection import detect_name_errors
from correction.names_correction import correct_names
from validation.names_validation import validate_names

def run_name_pipeline(df: pd.DataFrame, first_name_column, last_name_column) -> pd.DataFrame:
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
        first_name_column (str): Name of the column containing first names.
        last_name_column (str): Name of the column containing last names.

    Returns:
        pd.DataFrame: Updated DataFrame with additional columns for detected errors, corrections, and validation status.
    """
    
    ################################################################################
    # Step 1: Validate names
    df[[f"{first_name_column}_VALID", f"{last_name_column}_VALID"]] = df.apply(
        lambda row: pd.Series(
            validate_names(first_name=row[first_name_column], last_name=row[last_name_column])
        ),
        axis=1)

    print('df after validation:')
    print(df.head(5))
    print('#' * 50)
    
    ################################################################################
    # Step 2: Detect name and surname errors
    df[[f"{first_name_column}_DETECTED_ERRORS", f"{last_name_column}_DETECTED_ERRORS"]] = df.apply(
        lambda row: pd.Series(detect_name_errors(row[first_name_column], row[last_name_column])),
        axis=1
    )
    
    print('df after detection:')
    print(df.head(5))
    print('#' * 50)
    
    ################################################################################
    # Create columns to check if there are errors
    df[f'{first_name_column}_HAS_ERRORS'] = df[f"{first_name_column}_DETECTED_ERRORS"].apply(lambda x: len(x) > 0)
    df[f'{last_name_column}_HAS_ERRORS'] = df[f"{last_name_column}_DETECTED_ERRORS"].apply(lambda x: len(x) > 0)
    
    print('df after adding detection bool:')
    print(df.head(5))
    print('#' * 50)
    
    ################################################################################
    # Step 3: Correct if errors detected
    df[[f"{first_name_column}_CORRECTED", f"{first_name_column}_CORRECTED_ERRORS", f"{first_name_column}_UNCORRECTED_ERRORS",
        f"{last_name_column}_CORRECTED", f"{last_name_column}CORRECTED_ERRORS", f"{last_name_column}_UNCORRECTED_ERRORS"]] = df.apply(
        lambda row: pd.Series(correct_names(
            first_name=row[first_name_column],
            last_name=row[last_name_column],
            detected_first_name_errors=row[f"{first_name_column}_DETECTED_ERRORS"],
            detected_last_name_errors=row[f"{last_name_column}_DETECTED_ERRORS"],
        )) if (len(row[f"{first_name_column}_DETECTED_ERRORS"]) > 0 or len(row[f"{last_name_column}_DETECTED_ERRORS"]) > 0)
        else pd.Series([None, [], [], None, [], []])
        , axis=1
    )
    
    print('df after correction:')
    print(df.head(5))
    print('#' * 50)
    
    ################################################################################
    # Create columns to check which rows were corrected
    df[f"{first_name_column}_WAS_CORRECTED"] = df[f"{first_name_column}_CORRECTED"].notnull()
    df[f"{last_name_column}_WAS_CORRECTED"] = df[f"{last_name_column}_CORRECTED"].notnull()
    
    print('df after adding correction bool:')
    print(df.head(5))
    print('#' * 50)
    ################################################################################
    
    ################################################################################
    # Step 4: Re-validate for corrected names
    df[f"{first_name_column}_VALID_AFTER_CORRECTION"] = df.apply(
        lambda row: validate_names(first_name=row[f"{first_name_column}_CORRECTED"]) 
        if row[f"{first_name_column}_WAS_CORRECTED"] else None,
        axis=1
    )
    
    df[f"{last_name_column}_VALID_AFTER_CORRECTION"] = df.apply(
    lambda row: validate_names(first_name=row[f"{last_name_column}_CORRECTED"]) 
    if row[f"{last_name_column}_WAS_CORRECTED"] else None,
    axis=1
    )
    
    print('df after second validation:')
    print(df.head(5))
    df.to_excel("src/processed_data/04_pipeline_names_5.xlsx", index=False)
    print('#' * 50)
    
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
    
    df[f"{first_name_column}_STATUS"] = df.apply(lambda row: status(row, first_name_column), axis=1)
    df[f"{last_name_column}_STATUS"] = df.apply(lambda row: status(row, last_name_column), axis=1)
    
    return df

if __name__ == "__main__":
    # Load customer data
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Run the name pipeline
    df = run_name_pipeline(df, "FIRST_NAME", "LAST_NAME")

    # choose the columns to keep
    # columns_to_keep = [ ]
    # df = df[columns_to_keep]

    # Save updated file
    df.to_excel("src/processed_data/05_names.xlsx", index=False)
    print("Name pipeline completed successfully.")
