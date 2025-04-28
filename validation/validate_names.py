import pandas as pd
import requests

def fetch_SURS_data():
    """
    Fetch and process SURS data for Slovenian names and surnames.
    
    Args:
        None
        
    Returns:
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

def validate_names(first_name=None, last_name=None):
    """
    Validate first and last names against SURS data.
    
    Args:
        first_name (str, optional): First name to validate.
        last_name (str, optional): Last name to validate.
    
    Returns:
        tuple: (first_name_valid, last_name_valid)
            - first_name_valid (bool): True if the first name is valid, False otherwise.
            - last_name_valid (bool): True if the last name is valid, False otherwise.
    """
    if first_name is None and last_name is None:
        raise ValueError("At least one of first_name or last_name must be provided.")
    
    # Fetch SURS data only once
    if not hasattr(validate_names, "all_names"):
        print("Fetching SURS data...")
        validate_names.all_names, validate_names.all_surnames = fetch_SURS_data()
    
    all_names = validate_names.all_names
    all_surnames = validate_names.all_surnames
    
    if all_names is None or all_surnames is None:
        raise ValueError("Failed to fetch SURS data.")
    
    first_name_valid = None
    last_name_valid = None

    if first_name:
        first_name_valid = not all_names[all_names["value"] == first_name].empty
    
    if last_name:
        last_name_valid = not all_surnames[all_surnames["value"] == last_name].empty
    
    if first_name and last_name:
        return first_name_valid, last_name_valid
    elif first_name:
        return first_name_valid
    elif last_name:
        return last_name_valid

if __name__ == "__main__":
    customer_data = "src/processed_data/customer_data_with_errors.xlsx"
    customer_data = "src/processed_data/04_pipeline_names_4.xlsx"
    
    df = pd.read_excel(customer_data)

    # Apply validation and expand results into two new columns
    # df[["FIRST_NAME_VALID", "LAST_NAME_VALID"]] = df.apply(
    #     lambda row: pd.Series(
    #         validate_names(first_name=row["FIRST_NAME"], last_name=row["LAST_NAME"])
    #     ),
    #     axis=1)
    
    # Apply validation and expand results into two new columns
    # df["FIRST_NAME_VALID"] = df.apply(
    #     lambda row: pd.Series(
    #         validate_names(first_name=row["FIRST_NAME"])
    #     ),
    #     axis=1)
    
    
    df["corrected_first_name_VALID"] = df.apply(
        lambda row: pd.Series(
            validate_names(first_name=row["corrected_first_name"])
        ),
        axis=1)
    
    print(df)
    
    df.to_excel("src/processed_data/01_validated_names_test2.xlsx", index=False)

    # df.to_excel("src/processed_data/01_validated_names_test.xlsx", index=False)
