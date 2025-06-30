import pandas as pd
import os
import json

EXCEL_PATH = "src/raw_data/user_error_config.xlsx"
JSON_PATH = "src/raw_data/user_error_config.json"

def load_error_config_from_excel(path=EXCEL_PATH) -> dict:
    """
    Load the user-defined error config from Excel and convert to a dict.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"❌ Config file not found at: {path}")

    df = pd.read_excel(path, sheet_name="Sheet1")

    required_columns = {"error_code", "error_message", "detect", "correct", "dq_dimension"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Excel must contain columns: {required_columns}")

    config = {}
    for _, row in df.iterrows():
        code = str(row["error_code"])
        config[code] = {
            "error_message": row["error_message"],
            "detect": bool(row["detect"]),
            "correct": bool(row["correct"]),
            "dq_dimension": row["dq_dimension"]
        }

    return config

def ensure_config():
    """
    Always generate the JSON config from Excel and overwrite the existing file, even if it already exists.
    """
    print("Generating JSON config from Excel...")
    config = load_error_config_from_excel(EXCEL_PATH)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    print(f"Config created at: {JSON_PATH}")

load_error_config_from_excel(path=EXCEL_PATH)
ensure_config()

def load_error_config(path: str = JSON_PATH) -> dict:
    """Always regenerate and load the error config from Excel."""
    config = load_error_config_from_excel(EXCEL_PATH)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    return config

def should_detect(code, config):
    return config.get(code, {}).get("detect", True)

def should_correct(code, config):
    return config.get(code, {}).get("correct", True)

def get_message(code, config):
    return config.get(code, {}).get("error_message", "Unknown Error")
