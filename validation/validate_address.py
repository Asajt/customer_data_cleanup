import pandas as pd
import unidecode

# Function to normalize addresses
def normalize_address(address):
    return unidecode.unidecode(str(address)).strip().lower()

def validate_full_address(customer_full_address, path_to_gurs_RN_csv):
    """
    Validate customer addresses against GURS data.
    Args:
        customer_df (pd.DataFrame): DataFrame containing full customer addresses.
        gurs_df (pd.DataFrame): DataFrame containing full GURS addresses.
    Returns:
        pd.DataFrame: DataFrame with validated addresses.
    """

    # Load and prepare GURS data
    gurs_df = pd.read_csv(path_to_gurs_RN_csv, usecols = ['ULICA_NAZIV','HS_STEVILKA','HS_DODATEK','POSTNI_OKOLIS_SIFRA','POSTNI_OKOLIS_NAZIV'])
    # Remove dvojezična imena from POSTNI_OKOLIS_NAZIV
    gurs_df['POSTNI_OKOLIS_NAZIV'] = gurs_df['POSTNI_OKOLIS_NAZIV'].str.split('-').str[0].str.strip()
    
    gurs_df["GURS_FULL_ADDRESS"] = (
        gurs_df["ULICA_NAZIV"].str.strip() + " " +
        gurs_df["HS_STEVILKA"].fillna("").astype(str).str.strip() +
        gurs_df["HS_DODATEK"].fillna("").astype(str).str.strip() + ", " +
        gurs_df["POSTNI_OKOLIS_SIFRA"].fillna("").astype(str).str.strip() + " " +
        gurs_df["POSTNI_OKOLIS_NAZIV"].str.strip()
    )
    
    # Normalize GURS addresses
    gurs_df["GURS_normalized_address"] = gurs_df["GURS_FULL_ADDRESS"].apply(normalize_address)
    # keep only relevant columns
    gurs_df = gurs_df[["GURS_normalized_address"]]
    # Remove duplicates
    gurs_df = gurs_df.drop_duplicates(subset=["GURS_normalized_address"])

    # Load customer data    
    customer_df["customer_normalized_address"] = customer_full_address.apply(normalize_address)
    
    # Merge to get GURS match
    merged_df = customer_df.merge(
        gurs_df,
        how="left",
        left_on="customer_normalized_address",
        right_on="GURS_normalized_address",
    )

    merged_df["VALIDATED"] = merged_df["GURS_normalized_address"].notnull()

    return merged_df

# Load customer data
customer_df = pd.read_excel("src/processed_data/customer_data_with_errors.xlsx")
customer_df["FULL_ADDRESS"] = (
    customer_df["STREET"].str.strip() + " " +
    customer_df["HOUSE_NUMBER"].str.strip() + ", " +
    customer_df["POSTAL_CODE"].str.strip() + " " +
    customer_df["POSTAL_CITY"].str.strip()
)


df = validate_full_address(
    customer_full_address=customer_df["FULL_ADDRESS"],
    path_to_gurs_RN_csv="src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv"
)

print(df.head())