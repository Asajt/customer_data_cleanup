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
    ...
    # Apply validation and expand results into two new columns
    df[["FIRST_NAME_VALID", "LAST_NAME_VALID"]] = df.apply(
        lambda row: pd.Series(
            validate_names(first_name=row["FIRST_NAME"], last_name=row["LAST_NAME"])
        ),
        axis=1)

    print('df after validation:')
    print(df.head(10))
    print('#' * 50)
    ################################################################################
    
    ################################################################################
    # Step 2: Detect name + surname errors
    detection_results = df.apply(
        lambda row: pd.Series(detect_name_errors(row["FIRST_NAME"], row["LAST_NAME"])),
        axis=1
    )

    df = pd.concat([df, detection_results], axis=1)
    print('df after validation:')
    print(df.head(10))
    df.to_excel("src/processed_data/04_pipeline_names_1.xlsx", index=False)
    print('#' * 50)
    
    ################################################################################
    # create columns to check if there are errors
    df['name_has_errors'] = df['name_detected_errors'].apply(lambda x: len(x) > 0)
    df['surname_has_errors'] = df['surname_detected_errors'].apply(lambda x: len(x) > 0)
    
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
    
    correction_results = df.apply(
        lambda row: pd.Series(correct_names(
            first_name=row['FIRST_NAME'],
            last_name=row['LAST_NAME'],
            detected_first_name_errors=row["name_detected_errors"],
            detected_last_name_errors=row["surname_detected_errors"]
        )) if (len(row['name_detected_errors']) > 0 or len(row['surname_detected_errors']) > 0)
        else pd.Series({
            "corrected_first_name": None,
            "corrected_last_name": None,
            "corrected_first_name_errors": [],
            "corrected_last_name_errors": []
        }),
        axis=1
    )
        

    # Merge the correction results
    df = pd.concat([df, correction_results], axis=1)
    print('df after correction:')
    print(df.head(10))
    df.to_excel("src/processed_data/04_pipeline_names_3.xlsx", index=False)
    print('#' * 50)
    
    
    df["was_name_corrected"] = df["corrected_first_name"].notnull()
    df["was_surname_corrected"] = df["corrected_last_name"].notnull()
    
    print('df after adding correction bool:')
    print(df.head(10))
    df.to_excel("src/processed_data/04_pipeline_names_4.xlsx", index=False)
    print('#' * 50)
    ################################################################################
    
    ################################################################################
    # Step 4: Re-validate for corrected names
    
    df["corrected_first_name_VALID"] = df.apply(
    lambda row: validate_names(first_name=row["corrected_first_name"]) 
    if row["was_name_corrected"] else None,
    axis=1
    )
    
    df["corrected_last_name_VALID"] = df.apply(
    lambda row: validate_names(first_name=row["corrected_last_name"]) 
    if row["was_surname_corrected"] else None,
    axis=1
    )
    
    print('df after second validation:')
    print(df.head(10))
    df.to_excel("src/processed_data/04_pipeline_names_5.xlsx", index=False)
    print('#' * 50)
    ################################################################################
    
    ################################################################################
    # Step 5: Assign status
    def name_status(row):
        if row["FIRST_NAME_VALID"]:
            return "VALID"
        if row["name_has_errors"] and len(row["name_detected_errors"]) == len(row["corrected_first_name_errors"]):
            return "CORRECTED" if row["corrected_first_name_VALID"] else "PARTIALLY_CORRECTED"
        if row["name_has_errors"] and len(row["corrected_first_name_errors"]) == 0:
            return "DETECTED"
        return "INVALID"

    def surname_status(row):
        if row["LAST_NAME_VALID"]:
            return "VALID"
        if row["surname_has_errors"] and len(row["surname_detected_errors"]) == len(row["corrected_last_name_errors"]):
            return "CORRECTED" if row["corrected_last_name_VALID"] else "PARTIALLY_CORRECTED"
        if row["surname_has_errors"] and len(row["corrected_last_name_errors"]) == 0:
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
    # columns_to_keep = [
    #     "CUSTOMER_ID", "NAME", "SURNAME", "name_detected_errors", "surname_detected_errors",
    #     "has_name_errors", "has_surname_errors", "name_corrected", "surname_corrected",
    #     "name_corrected_errors", "surname_corrected_errors", "was_name_corrected",
    #     "was_surname_corrected", "name_valid_after_correction", "surname_valid_after_correction",
    #     "NAME_STATUS", "SURNAME_STATUS"
    # ]
    # df = df[columns_to_keep]

    # Save updated file
    df.to_excel("src/processed_data/05_names.xlsx", index=False)
    print("Name pipeline completed successfully.")
