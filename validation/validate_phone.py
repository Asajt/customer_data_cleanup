import re
import pandas as pd

def is_valid_phone(phone: str) -> bool:
    if not isinstance(phone, str) or not phone.strip():
        return False

    # Match format: 00386 followed by 7 or 8 digits
    return bool(re.fullmatch(r"00386\d{8}", phone))

def validate_phone(df: pd.DataFrame, phone_column: str) -> pd.DataFrame:
    """
    Validate Slovenian phone numbers in a DataFrame.
    This function checks if the phone numbers in the specified column of the DataFrame are valid
    according to a regex pattern. It adds a new column to the DataFrame indicating whether each
    phone number is valid or not.

    Args:
        df (pd.DataFrame): DataFrame containing customer data.
        phone_column (str): Name of the column containing phone numbers.

    Returns:
        pd.DataFrame: DataFrame with additional columns for name validation.
    """
    df[f"{phone_column}_VALID"] = df[phone_column].apply(is_valid_phone)
    return df

if __name__ == "__main__":
    
    df = pd.read_excel("src/processed_data/customer_data_with_errors.xlsx")
    df = validate_phone(df, phone_column="PHONE_NUMBER")
    
    # choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", "PHONE_NUMBER", "PHONE_NUMBER_VALID"
    ]
    df = df[columns_to_keep]

    df.to_excel("src/processed_data/01_validated_phone.xlsx", index=False)
    print("Phone number validation complete.")
