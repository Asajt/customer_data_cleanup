import re
import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.errors_utils import should_correct, load_error_config

error_config = load_error_config()

def correct_name_errors(df):
    """Correct errors in NAME and SURNAME columns."""
    df["NAME"] = df["NAME"].apply(lambda x: re.sub(r'[^a-zA-Z\s\-]', '', x) if pd.notnull(x) else x)
    df["SURNAME"] = df["SURNAME"].apply(lambda x: re.sub(r'[^a-zA-Z\s\-]', '', x) if pd.notnull(x) else x)
    return df
