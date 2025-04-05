import pandas as pd

def validate_full_address(customer_df: pd.DataFrame, full_address_column: str, path_to_gurs_RN_csv: str) -> pd.DataFrame:
    """_summary_

    Args:
        customer_df (pd.DataFrame): DataFrame containing customer data.
        full_address_column (str): Name of the column containing the full address in format "street house_number, postal_code postal_city"
        path_to_gurs_RN_csv (str): Path to the GURS RN CSV file.

    Returns:
        pd.DataFrame: DataFrame with additional columns for full address validation.
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
    
    gurs_df = gurs_df[["GURS_FULL_ADDRESS"]]
    # Remove duplicates
    gurs_df = gurs_df.drop_duplicates(subset=["GURS_FULL_ADDRESS"])

    # Merge to get GURS match
    merged_df = customer_df.merge(
        gurs_df,
        how="left",
        left_on=full_address_column,
        right_on="GURS_FULL_ADDRESS",
    )

    merged_df[f"{full_address_column}_VALID"] = merged_df["GURS_FULL_ADDRESS"].notnull()

    return merged_df

if __name__ == "__main__":
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Apply the address validation
    df["FULL_ADDRESS"] = (
        df["STREET"].str.strip() + " " +
        df["HOUSE_NUMBER"].str.strip() + ", " +
        df["POSTAL_CODE"].str.strip() + " " +
        df["POSTAL_CITY"].str.strip()
    )

    df = validate_full_address(df,"FULL_ADDRESS",
        path_to_gurs_RN_csv="src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv")
    
    # choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", "FULL_ADDRESS", "GURS_FULL_ADDRESS", "FULL_ADDRESS_VALID"
    ]
    df = df[columns_to_keep]
    
    df.to_excel("src/processed_data/01_validated_address.xlsx", index=False)
    print("Address validation complete.")
