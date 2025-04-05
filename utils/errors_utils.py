import pandas as pd
import os

def load_error_config_from_excel(path="src/raw/user_correction_config.xlsx") -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Config file not found at: {path}")

    df = pd.read_excel(path, sheet_name="ErrorConfig")

    # Basic validation
    required_columns = {"error_code", "error_message", "detect", "correct"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Excel must contain columns: {required_columns}")

    config = {}
    for _, row in df.iterrows():
        code = str(row["error_code"])
        config[code] = {
            "error_message": row["error_message"],
            "detect": bool(row["detect"]),
            "correct": bool(row["correct"]),
        }

    return config

def should_detect(code, config):
    return config.get(code, {}).get("detect", False)

def should_correct(code, config):
    return config.get(code, {}).get("correct", False)

def get_message(code, config):
    return config.get(code, {}).get("error_message", "Unknown Error")


# USAGE 
# if should_detect('1104', error_config):
#     errors.add('1104')