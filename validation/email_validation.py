import pandas as pd
import regex as re

def validate_email(email) -> bool:
    """
    Validate an email address against a predefined set of domains.
    
    Args:
        email (str): The email address to validate.
        
    Returns:
        bool: True if the email is valid, False otherwise.
    """

    EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+-]+@(?:gmail\.com|siol\.net|amis\.net|t-2\.net|email\.si|zvpl\.com|hotmail\.com|outlook\.com|yahoo\.com|guest\.arnes\.si|volja\.net|[a-zA-Z0-9-]+\.(?:si))$"
    )
    
    if not isinstance(email, str) or not email.strip():
        return False
    return bool(EMAIL_REGEX.match(email))

if __name__ == "__main__":
    # Load customer data
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Validate emails
    df["EMAIL_VALID"] = df["EMAIL"].apply(validate_email)

    # Choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", "EMAIL", "EMAIL_VALID"
    ]
    df = df[columns_to_keep]
    
    # Save updated file
    df.to_excel("src/processed_data/01_validated_email.xlsx", index=False)
    print("Email validation completed successfully.")
