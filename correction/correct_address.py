import re
import pandas as pd

def correct_address_errors(df):
    """Correct errors in address components: street, house number, postal code, and city."""

    # Correct Street: Trim spaces & remove special chars
    df["STREET"] = df["STREET"].apply(lambda x: x.strip() if pd.notnull(x) else x)
    df["STREET"] = df["STREET"].apply(lambda x: re.sub(r'\s+', ' ', x) if pd.notnull(x) else x)
    df["STREET"] = df["STREET"].apply(lambda x: re.sub(r'[^a-zA-ZčćšžČĆŠŽ\s\.,-]', '', x) if pd.notnull(x) else x)

    # Correct House Number: Keep only numeric
    df["HOUSE_NUMBER"] = df["HOUSE_NUMBER"].apply(lambda x: re.sub(r'\D', '', x) if pd.notnull(x) else x)

    # Correct Postal Code: Trim spaces
    df["POSTAL_CODE"] = df["POSTAL_CODE"].apply(lambda x: x.strip() if pd.notnull(x) else x)

    return df
