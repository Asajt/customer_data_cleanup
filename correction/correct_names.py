import re
import pandas as pd

def correct_name_errors(df):
    """Correct errors in NAME and SURNAME columns."""
    df["NAME"] = df["NAME"].apply(lambda x: re.sub(r'[^a-zA-Z\s\-]', '', x) if pd.notnull(x) else x)
    df["SURNAME"] = df["SURNAME"].apply(lambda x: re.sub(r'[^a-zA-Z\s\-]', '', x) if pd.notnull(x) else x)
    return df
