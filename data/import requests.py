import requests
import pandas as pd

# Define API URLs and query
urls = {
    "female": "https://pxweb.stat.si/SiStatData/api/v1/sl/Data/05X1010S.px",
    "male": "https://pxweb.stat.si/SiStatData/api/v1/sl/Data/05X1005S.px"
}
query = {
    "query": [
        {
            "code": "MERITVE",
            "selection": {
                "filter": "item",
                "values": [
                    "1"  # Filter for "Število"
                ]
            }
        },
        {
            "code": "LETO",
            "selection": {
                "filter": "item",
                "values": [
                    "2024"  # Specific year
                ]
            }
        }
    ],
    "response": {
        "format": "json-stat"
    }
}

# Function to fetch and process data
def fetch_names_and_counts(url):
    response = requests.post(url, json=query)

    if response.status_code == 200:
        data = response.json()

        # Extract dimensions and values
        ime_category = data['dataset']['dimension']['IME']['category']
        names = ime_category['label']  # Extract names
        values = data['dataset']['value']  # Extract counts

        # Create a DataFrame
        df = pd.DataFrame({
            "name": list(names.values()),
            "count": values
        })

        return df
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return pd.DataFrame()  # Return empty DataFrame in case of failure

# Fetch data for both male and female names
female_names_df = fetch_names_and_counts(urls["female"])
male_names_df = fetch_names_and_counts(urls["male"])

# Combine both DataFrames
all_names_df = pd.concat([female_names_df, male_names_df], ignore_index=True)

# Calculate total count
total_count = all_names_df["count"].sum()

# Calculate frequency and remove count column
all_names_df["frequency"] = all_names_df["count"] / total_count
all_names_df = all_names_df.drop(columns=["count"])

# Display the updated DataFrame
print(all_names_df)
