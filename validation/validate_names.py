import pandas as pd
import requests

def fetch_SURS_data():
    """
    Fetch and process SURS data for Slovenian names and surnames.

    Returns:
    --------
    tuple (pd.DataFrame, pd.DataFrame)
        - all_names : DataFrame containing first names and their frequencies.
        - all_surnames : DataFrame containing last names and their frequencies.
    """
    
    query = {
    "query": [
        {"code": "MERITVE", "selection": {"filter": "item", "values": ["1"]}},
        {"code": "LETO", "selection": {"filter": "item", "values": ["2024"]}}
    ],
    "response": {"format": "json-stat"}
    }
    
    def fetch_data(url, key):
        response = requests.post(url, json=query)
        if response.status_code == 200:
            data = response.json()
            # Extract dimensions and values
            category = data['dataset']['dimension'][key]['category']
            labels = category['label']  # Extract names or surnames
            values = data['dataset']['value']  # Extract counts
            # Create a DataFrame
            df = pd.DataFrame({
                "value": list(labels.values()),
                "count": values
            })
            return df[["value", "count"]]
        else:
            print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
            return pd.DataFrame()

    # Combine all dataframes into one and calculate frequencies
    def calculate_frequencies(df):
        # Calculate total count
        total_count = df["count"].sum()
        # Calculate frequencies
        df["frequency"] = df.apply(
            lambda row: row["count"] / total_count if not pd.isna(row["count"]) else 0,
            axis=1)
        return df

    # Fetch and combine male and female names
    name_urls = {
        "female": "https://pxweb.stat.si/SiStatData/api/v1/sl/Data/05X1010S.px",
        "male": "https://pxweb.stat.si/SiStatData/api/v1/sl/Data/05X1005S.px"}
    female_names = fetch_data(name_urls["female"], key="IME")
    male_names = fetch_data(name_urls["male"], key="IME")
    all_names = pd.concat([female_names, male_names], ignore_index=True)
    
    surname_urls = [
        "https://pxweb.stat.si:443/SiStatData/api/v1/sl/Data/05X1015S.px",
        "https://pxweb.stat.si:443/SiStatData/api/v1/sl/Data/05X1016S.px",
        "https://pxweb.stat.si:443/SiStatData/api/v1/sl/Data/05X1017S.px",
        "https://pxweb.stat.si:443/SiStatData/api/v1/sl/Data/05X1018S.px"]
    surname_dataframes = [fetch_data(url, key="PRIIMEK") for url in surname_urls]
    all_surnames = pd.concat(surname_dataframes, ignore_index=True)

    # Calculate frequencies for names and surnames
    all_names = calculate_frequencies(all_names)
    all_surnames = calculate_frequencies(all_surnames)
    
    print("SURS data extracted")
    return all_names, all_surnames

def validate_names(customer_df: pd.DataFrame, first_name_column: str = None, last_name_column: str = None) -> pd.DataFrame:
    """
    Validate first and/or last names in a DataFrame against SURS data.
    
    Args:
        customer_df (pd.DataFrame): DataFrame containing customer data.
        first_name_column (str, optional): Name of the column containing first names.
        last_name_column (str, optional): Name of the column containing last names.

    Raises:
        ValueError: If SURS data fetching fails.

    Returns:
        pd.DataFrame: DataFrame with additional columns for name validation.
    """   
    
    if first_name_column is None and last_name_column is None:
        raise ValueError("At least one of first_name_column or last_name_column must be provided.")
    
    # Fetch SURS name and surname datasets
    all_names, all_surnames = fetch_SURS_data()

    if all_names is None or all_surnames is None:
        raise ValueError("Failed to fetch SURS data.")
    
    if first_name_column:    
        # dataframe of FIRST_NAME 
        first_names_df = pd.DataFrame(all_names["value"])
        first_names_df.columns = ["SURS_FIRST_NAME"]
    
        # Merge FIRST_NAME
        merged_df = customer_df.merge(
            first_names_df,
            how="left",
            left_on=first_name_column,
            right_on="SURS_FIRST_NAME",
        )
        merged_df[f"{first_name_column}_VALID"] = merged_df["SURS_FIRST_NAME"].notnull()
    
    if last_name_column:
        # dataframe of LAST_NAME
        last_names_df = pd.DataFrame(all_surnames["value"])
        last_names_df.columns = ["SURS_LAST_NAME"]

        # Merge LAST_NAME
        merged_df = merged_df.merge(
            last_names_df,
            how="left",
            left_on=last_name_column,
            right_on="SURS_LAST_NAME",
        )
        merged_df[f"{last_name_column}_VALID"] = merged_df["SURS_LAST_NAME"].notnull()

    return merged_df

if __name__ == "__main__":
    # Load customer data
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    df = pd.read_excel(customer_data)

    # Run name validation
    df = validate_names(df, "FIRST_NAME", "LAST_NAME")

  # choose the columns to keep
    columns_to_keep = [
        "CUSTOMER_ID", "FIRST_NAME", "SURS_FIRST_NAME",  "FIRST_NAME_VALID", "LAST_NAME", "SURS_LAST_NAME", "LAST_NAME_VALID"
    ]
    df = df[columns_to_keep]
    
    # Save updated file
    df.to_excel("src/processed_data/01_validated_namess.xlsx", index=False)
    print("Name validation complete.")

