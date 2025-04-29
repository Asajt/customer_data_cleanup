import re
import pandas as pd


def validate_phone(phone: str) -> bool:
    """
    This function validates Slovenian phone numbers.
    It checks if the phone number starts with "00386" and is followed by 7 or 8 digits.
    The function returns True if the phone number is valid, otherwise it returns False.
    Args:
        phone (str): Phone number to validate.
    Returns:
        bool: True if the phone number is valid, False otherwise.
    """
    
    if not isinstance(phone, str) or not phone.strip():
        return False

    # Match format: 00386 followed by 7 or 8 digits
    return bool(re.fullmatch(r"00386\d{8}", phone))

if __name__ == "__main__":
    
    df = pd.read_excel("src/processed_data/customer_data_with_errors.xlsx")
    
    # Validate phone numbers
    df["PHONE_NUMBER_VALID"] = df["PHONE_NUMBER"].apply(validate_phone)
    
    # choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", "PHONE_NUMBER", "PHONE_NUMBER_VALID"
    ]
    df = df[columns_to_keep]

    df.to_excel("src/processed_data/01_validated_phone.xlsx", index=False)
    print("Phone number validation complete.")
