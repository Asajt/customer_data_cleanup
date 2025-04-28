import pandas as pd

def load_gurs_data(path_to_gurs_RN_csv: str) -> pd.DataFrame:
    """
    Load GURS RN data from a CSV file and prepare it for validation.
    This function loads the GURS RN data, cleans the POSTNI_OKOLIS_NAZIV column,
    and creates a full address column for validation.

    Args:
        path_to_gurs_RN_csv (str): Path to the GURS RN CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the cleaned GURS RN data.
    """
    
    # Load and prepare GURS data
    gurs_df = pd.read_csv(path_to_gurs_RN_csv, usecols = ['ULICA_NAZIV','HS_STEVILKA','HS_DODATEK','POSTNI_OKOLIS_SIFRA','POSTNI_OKOLIS_NAZIV'])
    print("GURS data loaded.")
    
    # Remove dvojezična imena from POSTNI_OKOLIS_NAZIV
    gurs_df['POSTNI_OKOLIS_NAZIV'] = gurs_df['POSTNI_OKOLIS_NAZIV'].str.split('-').str[0].str.strip()
    print("POSTNI_OKOLIS_NAZIV cleaned.")
    
    gurs_df["GURS_FULL_ADDRESS"] = (
        gurs_df["ULICA_NAZIV"].str.strip() + " " +
        gurs_df["HS_STEVILKA"].fillna("").astype(str).str.strip() +
        gurs_df["HS_DODATEK"].fillna("").astype(str).str.strip() + ", " +
        gurs_df["POSTNI_OKOLIS_SIFRA"].fillna("").astype(str).str.strip() + " " +
        gurs_df["POSTNI_OKOLIS_NAZIV"].str.strip()
    )
    print("GURS_FULL_ADDRESS created.")
    
    gurs_df = gurs_df[["GURS_FULL_ADDRESS"]]
    
    # Make a set of GURS_FULL_ADDRESS for faster lookup
    gurs_address_set = set(gurs_df['GURS_FULL_ADDRESS'].dropna().str.strip())
    print("GURS_FULL_ADDRESS set created.")
    
    return gurs_address_set

def validate_full_address(full_address: str, gurs_address_set: set) -> bool:
    """
    Validate the full address against the GURS address set.
    This function checks if the provided full address is present in the GURS address set.
    
    Args:
        full_address (str): Full address to validate.
        gurs_address_set (set): Set of valid GURS addresses.
    
    Returns:
        bool: True if the full address is valid, False otherwise.
    """    
    
    # If the full_address_column value is not in the gurs_address_set, it is invalid, so we set it to False
    if pd.isna(full_address):
        return False
    return full_address.strip() in gurs_address_set

if __name__ == "__main__":
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Create FULL_ADDRESS
    df["FULL_ADDRESS"] = (
        df["STREET"].str.strip() + " " +
        df["HOUSE_NUMBER"].str.strip() + ", " +
        df["POSTAL_CODE"].str.strip() + " " +
        df["POSTAL_CITY"].str.strip()
    )
    
    # Load GURS data ONCE
    gurs_address_set = load_gurs_data("src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv")
    
    # Apply validation
    df["FULL_ADDRESS_VALID"] = df["FULL_ADDRESS"].apply(lambda addr: validate_full_address(addr, gurs_address_set))

    # Save only desired columns
    columns_to_keep = [
        "CUSTOMER_ID", "FULL_ADDRESS", "FULL_ADDRESS_VALID"
    ]
    df = df[columns_to_keep]

    print(df.head(10))
    print("Address validation complete.")
    # df.to_excel("src/processed_data/01_validated_address.xlsx", index=False)
