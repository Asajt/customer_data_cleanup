import uuid
import pandas as pd
import numpy as np



# Initialize an empty error log
error_log = pd.DataFrame(columns=['Error_ID', 'Error_Type', 'Column_Affected', 'Original_Value', 'New_Value', 'Row_ID'])

def log_error(error_type, column, original_value, new_value, row_id):
    global error_log
    error_log = pd.concat([
        error_log,
        pd.DataFrame([{
            "Error_ID": str(uuid.uuid4()),  # Unique error identifier
            "Error_Type": error_type,
            "Column_Affected": column,
            "Original_Value": original_value,
            "New_Value": new_value,
            "Row_ID": row_id
        }])
    ], ignore_index=True)
    
    
# 3. Modify Error Injection Functions to Track Changes
# Update the error injection functions to log every modification.
# Example: Introduce Missing Data
def introduce_missing_data_with_logging(df, missing_rate=0.1):
    for col in df.columns:
        if df[col].dtype != 'object':  # Exclude non-numerical columns
            mask = np.random.rand(len(df)) < missing_rate
            for index in df[mask].index:
                original_value = df.at[index, col]
                df.at[index, col] = np.nan  # Introduce missing value
                log_error("Missing Data", col, original_value, np.nan, index)
    return df

# Example: Inject Invalid Values
def inject_invalid_values_with_logging(df):
    # Replace some postal codes with invalid values
    invalid_postal_codes = ["ABC", "00000", "99999"]
    indices = np.random.choice(df.index, size=10, replace=False)
    for index in indices:
        original_value = df.at[index, 'POSTAL_CODE']
        new_value = np.random.choice(invalid_postal_codes)
        df.at[index, 'POSTAL_CODE'] = new_value
        log_error("Invalid Value", "POSTAL_CODE", original_value, new_value, index)
    
    # Replace some phone numbers with invalid formats
    indices = np.random.choice(df.index, size=10, replace=False)
    for index in indices:
        original_value = df.at[index, 'PHONE_NUMBER']
        new_value = np.random.choice(["INVALID", "+123456", "555-555"])
        df.at[index, 'PHONE_NUMBER'] = new_value
        log_error("Invalid Value", "PHONE_NUMBER", original_value, new_value, index)
    
    return df

# Example: Duplicate Data
def introduce_duplicates_with_logging(df, duplicate_rate=0.05):
    num_duplicates = int(len(df) * duplicate_rate)
    duplicates = df.sample(num_duplicates, replace=True)
    
    for index in duplicates.index:
        log_error("Duplicate Row", None, None, "Duplicated Row", index)
    
    return pd.concat([df, duplicates]).reset_index(drop=True)


# 4. Track All Errors
# After all modifications, the error_log DataFrame will contain a complete record of all introduced errors. You can export this log for documentation or debugging purposes.
error_log.to_csv("error_log.csv", index=False)


# 5. Example Workflow
# Here's how a full workflow might look:
# Apply modifications with logging

# customer_df = introduce_missing_data_with_logging(customer_df, missing_rate=0.1)
# customer_df = inject_invalid_values_with_logging(customer_df)
# customer_df = introduce_duplicates_with_logging(customer_df, duplicate_rate=0.05)

# Save the modified dataset and error log
# customer_df.to_csv("chaos_engineered_customer_data.csv", index=False)
error_log.to_csv("error_log.csv", index=False)