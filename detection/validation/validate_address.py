import pandas as pd
import unidecode

# Normalize helper
def normalize_address(address):
    return unidecode.unidecode(str(address)).strip().lower()

# Load customer data
customer_df = pd.read_excel("src/processed_data/customer_data_with_errors.xlsx")
customer_df["FULL_ADDRESS"] = (
    customer_df["STREET"].str.strip() + " " +
    customer_df["HOUSE_NUMBER"].str.strip() + ", " +
    customer_df["POSTAL_CODE"].str.strip() + " " +
    customer_df["POSTAL_CITY"].str.strip()
)
customer_df["customer_normalized_address"] = customer_df["FULL_ADDRESS"].apply(normalize_address)
print("Customer data loaded and normalized")

# Load GURS data
gurs_df = pd.read_csv("src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv")
gurs_df["GURS_FULL_ADDRESS"] = (
    gurs_df["ULICA_NAZIV"].str.strip() + " " +
    gurs_df["HS_STEVILKA"].fillna("").astype(str).str.strip() +
    gurs_df["HS_DODATEK"].fillna("").astype(str).str.strip() + ", " +
    gurs_df["POSTNI_OKOLIS_SIFRA"].fillna("").astype(str).str.strip() + " " +
    gurs_df["POSTNI_OKOLIS_NAZIV"].str.strip()
)
gurs_df["GURS_normalized_address"] = gurs_df["GURS_FULL_ADDRESS"].apply(normalize_address)
print("GURS data loaded and normalized")


# keep only relevant columns
gurs_df = gurs_df[["GURS_normalized_address"]]
customer_df = customer_df[["CUSTOMER_ID", "customer_normalized_address"]]

# Remove duplicates
gurs_df = gurs_df.drop_duplicates(subset=["GURS_normalized_address"])

# Merge only to get GURS match
merged_df = customer_df.merge(
    gurs_df,
    how="left",
    left_on="customer_normalized_address",
    right_on="GURS_normalized_address",
)

merged_df["VALIDATED"] = merged_df["GURS_normalized_address"].notnull()

# Export relevant fields
merged_df.to_excel("src/processed_data/validated_addresses.xlsx", index=False)

print("Validation with GURS match completed and saved to validated_addresses.xlsx")
