import pandas as pd
from detection.name_detection import detect_name_errors
from correction.name_correction import correct_name_errors
from validation.validate_name import validate_name


def run_name_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    # Step 1: Detect name + surname errors
    errors_df = df.apply(lambda row: pd.Series(detect_name_errors(row["name"], row["surname"])), axis=1)
    df["name_detected_errors"] = errors_df["name_errors"]
    df["surname_detected_errors"] = errors_df["surname_errors"]
    df["has_name_errors"] = df["name_detected_errors"].apply(lambda x: len(x) > 0)
    df["has_surname_errors"] = df["surname_detected_errors"].apply(lambda x: len(x) > 0)

    # Step 2: Correct
    def correct(row):
        if row["has_name_errors"] or row["has_surname_errors"]:
            result = correct_name_errors(
                row["name"], row["surname"],
                row["name_detected_errors"], row["surname_detected_errors"]
            )
        else:
            result = {
                "name_corrected": row["name"],
                "surname_corrected": row["surname"],
                "name_corrected_errors": [],
                "surname_corrected_errors": []
            }
        return pd.Series(result)

    correction_df = df.apply(correct, axis=1)
    df = pd.concat([df, correction_df], axis=1)
    df["was_name_corrected"] = df["name_corrected_errors"].apply(lambda x: len(x) > 0)
    df["was_surname_corrected"] = df["surname_corrected_errors"].apply(lambda x: len(x) > 0)

    # Step 3: Re-validate (only if fully corrected)
    def validate_if_corrected(row):
        results = {"name_valid_after_correction": None, "surname_valid_after_correction": None}
        if len(row["name_detected_errors"]) == len(row["name_corrected_errors"]):
            results["name_valid_after_correction"] = validate_name(row["name_corrected"], row["surname_corrected"])["name_valid"]
        if len(row["surname_detected_errors"]) == len(row["surname_corrected_errors"]):
            results["surname_valid_after_correction"] = validate_name(row["name_corrected"], row["surname_corrected"])["surname_valid"]
        return pd.Series(results)

    validation_df = df.apply(validate_if_corrected, axis=1)
    df = pd.concat([df, validation_df], axis=1)

    # Step 4: Assign status
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

    return df
