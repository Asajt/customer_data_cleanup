import re
import pandas as pd

def detect_name_errors(df):
    """Detect errors in NAME and SURNAME columns."""
    pattern = r'[^a-zA-Z\s\-]'
    df["Name_Error"] = df["NAME"].apply(lambda x: bool(re.search(pattern, x)) if pd.notnull(x) else False)
    df["Surname_Error"] = df["SURNAME"].apply(lambda x: bool(re.search(pattern, x)) if pd.notnull(x) else False)
    return df
