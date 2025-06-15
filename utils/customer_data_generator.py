import pandas as pd
import requests
import numpy as np
import unidecode

def fetch_GURS_data(file_path):
    """
    Fetch and process GURS address data.

    Parameters:
    -----------
    file_path : str
        Path to the CSV file containing GURS data.

    Returns:
    --------
    pd.DataFrame
        Processed address data containing relevant columns.
    """
    addresses = pd.read_csv(file_path)

    addresses = addresses[addresses['ULICA_NAZIV'].notna() & addresses['ULICA_NAZIV'].str.strip().ne('')]

    columns_to_keep = ['EID_NASLOV'
                    ,'OBCINA_NAZIV'
                    ,'NASELJE_NAZIV'
                    ,'ULICA_NAZIV'
                    ,'POSTNI_OKOLIS_SIFRA'
                    ,'POSTNI_OKOLIS_NAZIV'
                    ,'HS_STEVILKA'
                    ,'HS_DODATEK'
                    ,'ST_STANOVANJA']
    addresses = addresses[columns_to_keep]

    addresses['ST_STANOVANJA'] = addresses['ST_STANOVANJA'].astype('Int64')

    print("GURS data extracted")
    return addresses

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
  
def generate_slo_phone_number():
    """
    Generate a random Slovenian phone number.

    Returns:
    --------
    str
        A valid Slovenian phone number in the format '00386XXXXXXXX'.
    """
    
    country_code = "00386"
    mobile_prefixes = ['1', '30', '31', '40', '41', '51', '64', '65', '68', '70']
    # Randomly choose a mobile prefix
    prefix = np.random.choice(mobile_prefixes)
    # Generate the rest of the number, depending if its 01 or smthing else
    if len(prefix) == 2:
        number = f"{np.random.randint(100000, 1000000)}"
    else:
        number = f"{np.random.randint(1000000, 10000000)}"
    # Combine to form the full phone number
    phone_number = f"{country_code}{prefix}{number}"
    
    return phone_number

def generate_random_email(first_name, last_name, seed=42):
    """
    Generate a realistic random email based on the given first and last names.

    Parameters:
    -----------
    first_name : str
        The user's first name.
    last_name : str
        The user's last name.

    Returns:
    --------
    str
        A randomly generated email address.
    """
    
    # Set random seed for reproducibility
    np.random.seed(seed)
    
    domains = ['gmail.com', 'hotmail.com', 'yahoo.com', 'icloud.com', 'siol.net', 't-2.net', 'amis.net', 'guest.arnes.net']
    domain_weights = [0.4, 0.2, 0.2, 0.1, 0.05, 0.025, 0.015, 0.01]  # Weights for each domain
    # Clean and sanitize names
    clean_first_name = unidecode.unidecode(first_name).lower().replace(" ", "")
    clean_last_name = unidecode.unidecode(last_name).lower().replace(" ", "")
    # Choose a random format for the email
    formats = [
        f"{clean_first_name}.{clean_last_name}",
        f"{clean_first_name}{clean_last_name}",
        f"{clean_first_name[0]}.{clean_last_name}"]
    email_base = np.random.choice(formats)
    # Add a unique ID with some probability
    if np.random.rand() > 0.7:  # 30% chance to add a number
        email_base += str(np.random.randint(1, 100))
    # Select a domain with weighted probability
    domain = np.random.choice(domains, p=domain_weights)
    
    return f"{email_base}@{domain}"

def generate_synthetic_customer_data(gurs_file_path, dataset_size = 10000, seed = 42):
    """
    Generate a synthetic customer dataset using GURS and SURS data.

    Parameters:
    -----------
    gurs_file_path : str
        Path to the GURS address data CSV file.
    dataset_size : int
        Number of synthetic customer records to generate.
    seed : int, default=42
        Random seed for reproducibility.

    Returns:
    --------
    pd.DataFrame
        Generated synthetic customer dataset.
    """
    
    # Set random seed for reproducibility
    np.random.seed(seed)

    addresses = fetch_GURS_data(gurs_file_path)
    all_names, all_surnames = fetch_SURS_data()
    
    
    # Randomly sample names and surnames based on their frequencies
    random_names = np.random.choice(
        all_names["value"],
        size=dataset_size,
        p=all_names["frequency"])
    random_surnames = np.random.choice(
        all_surnames["value"],
        size=dataset_size,
        p=all_surnames["frequency"])
    random_addresses = addresses.sample(dataset_size, replace=True).reset_index(drop=True)

    customer_df = pd.DataFrame({
        'CUSTOMER_ID': np.arange(1, dataset_size + 1)
        ,'FIRST_NAME': random_names
        ,'LAST_NAME': random_surnames
        ,'STREET': random_addresses['ULICA_NAZIV']
        ,'HN': random_addresses['HS_STEVILKA']
        ,'HN_ADDITION': random_addresses['HS_DODATEK'].apply(lambda x: str(x).upper() if pd.notna(x) else "")
        ,'APARTMENT_NUMBER': random_addresses['ST_STANOVANJA']
        ,'POSTAL_CODE': random_addresses['POSTNI_OKOLIS_SIFRA']
        ,'POSTAL_CITY': random_addresses['POSTNI_OKOLIS_NAZIV']
        ,'COUNTRY': 'Slovenia'
        ,'PHONE_NUMBER': [generate_slo_phone_number() for i in range(dataset_size)]
    })

    customer_df['EMAIL'] = [generate_random_email(name, surname) for name, surname in zip(random_names, random_surnames)]

    # Combine 'HOUSE_NUMBER' and 'HOUSE_NUMBER_ADDITION' into 'HOUSE_NUMBER_FULL' without spaces
    customer_df['HOUSE_NUMBER'] = customer_df['HN'].astype(str) + customer_df['HN_ADDITION']
    customer_df.drop(columns=['HN', 'HN_ADDITION'], inplace=True)

    # Clean up POSTAL_CITY by removing anything after "-"
    customer_df['POSTAL_CITY'] = customer_df['POSTAL_CITY'].str.split('-').str[0].str.strip()


    columns_order = ['CUSTOMER_ID', 'FIRST_NAME', 'LAST_NAME', 'STREET', 'HOUSE_NUMBER', 
                    'APARTMENT_NUMBER', 'POSTAL_CODE', 'POSTAL_CITY', 'COUNTRY', 'PHONE_NUMBER', 'EMAIL']
    customer_df = customer_df[columns_order]

        
    return customer_df

if __name__ == "__main__":
    # Example usage
    GURS_file_path = 'src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv'
    customer_df = generate_synthetic_customer_data(GURS_file_path, dataset_size=10000, seed=42)
    print("Synthetic customer dataset generated")
    customer_df.to_excel("src/processed_data/customer_data.xlsx", index=False)
