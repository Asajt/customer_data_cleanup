import pandas as pd
from tqdm import tqdm
from email_validator import validate_email as email_validator, EmailNotValidError

def validate_email(email) -> bool:
    """
    Validate an email address using the email-validator package.
    
    Args:
        email (str): The email address to validate.
        
    Returns:
        bool: True if the email is valid, False otherwise.
    """
    try:
        if not isinstance(email, str) or not email.strip():
            return False
        email_validator(email)
        return True
    except EmailNotValidError:
        return False

if __name__ == "__main__":
    # Load customer data
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Add tqdm progress bar to the apply function
    tqdm.pandas(desc="Validating emails")
    # Validate emails
    df["EMAIL_VALID"] = df["EMAIL"].progress_apply(validate_email)

    # Choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", "EMAIL", "EMAIL_VALID"
    ]
    df = df[columns_to_keep]
    
    # Save updated file
    df.to_excel("src/processed_data/01_validated_email.xlsx", index=False)
    print("Email validation completed successfully.")
