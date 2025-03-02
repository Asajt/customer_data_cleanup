import pandas as pd

def extract_allowed_characters(df, column="STREET_NAME"):
    """
    Extracts all unique characters present in the specified column.
    
    Parameters:
    - df (pd.DataFrame): The dataset containing address data.
    - column (str): The column to analyze (default: "STREET_NAME").
    
    Returns:
    - set: A set of all unique allowed characters in the column.
    """
    all_chars = set()

    # Iterate over each street name
    for street in df[column].dropna().unique():  # Remove NaN values
        all_chars.update(set(street))  # Extract characters

    return all_chars

# Example usage:
# Load dataset
df = pd.read_csv("/Users/tjasagrabnar/Desktop/magistrska/RN_SLO_NASLOVI_register_naslovov_20240929.csv", dtype=str)  # Ensure data is treated as strings

# Extract allowed characters
allowed_chars = extract_allowed_characters(df, column="ULICA_NAZIV")

# Display results
print("Allowed characters in ULICA_NAZIV:", allowed_chars)