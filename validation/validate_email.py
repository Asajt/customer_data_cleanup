import pandas as pd
import re

def is_valid_email(email: str) -> bool:
    EMAIL_REGEX = re.compile(
    r"^[a-žA-Ž0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    
    if not isinstance(email, str) or not email.strip():
        return False
    return bool(EMAIL_REGEX.match(email))

def validate_email(customer_df: pd.DataFrame, email_column: str) -> pd.DataFrame:
    """_summary_

    Args:
        customer_df (pd.DataFrame): DataFrame containing customer data.
        email_column (str): Name of the column containing email addresses.

    Returns:
        pd.DataFrame: DataFrame with additional columns for email validation.
    """
    customer_df["EMAIL_VALID"] = customer_df[email_column].apply(is_valid_email)
    return customer_df


if __name__ == "__main__":
    # Load customer data
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Run email validation
    df = validate_email(df, "EMAIL")

    # Save updated file
    df.to_excel("src/processed_data/customer_data_with_email_validation.xlsx", index=False)