import numpy as np
import pandas as pd
import time
from collections import Counter
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, precision_recall_fscore_support
from pipelines.master_pipeline import run_full_quality_pipeline
from utils.customer_data_generator import generate_synthetic_customer_data
from utils.chaos_engineering import apply_errors
from utils.errors_utils import should_detect, load_error_config, should_correct
import os

# Parameters
GURS_file_path = 'src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv'
dataset_size = 10000
seed = 7 #42
cache_path = f"src/cache/final_customer_data_{dataset_size}_{seed}.parquet"

time_measurement = False
use_cache_result = True
cache_result = False
evaluate_model = True
generate_report = False

###################################################### Main execution ######################################################


if use_cache_result and os.path.exists(cache_path):
    print(f"Loading cached DataFrame from {cache_path}")
    df = pd.read_parquet(cache_path)
else:
    print("Generating and processing data from scratch...")    
    # generate synthetic customer data
    df = generate_synthetic_customer_data(GURS_file_path, dataset_size, seed)

    # introduce errors into the dataset
    df = apply_errors(df, seed)

    start_time = time.time()
    # Run the full quality pipeline
    run_full_quality_pipeline(df, 
                                first_name_column="FIRST_NAME", 
                                last_name_column="LAST_NAME", 
                                street_column="STREET", 
                                street_number_column="HOUSE_NUMBER", 
                                postal_code_column="POSTAL_CODE", 
                                postal_city_column="POSTAL_CITY", 
                                email_column="EMAIL", 
                                phone_column="PHONE_NUMBER")
    end_time = time.time()
    elapsed_time = end_time - start_time
    # Cache DataFrame for future fast loading
    if cache_result:
        cache_path = f"src/cache/final_customer_data_{dataset_size}_{seed}.parquet"
        df.to_parquet(cache_path, index=False)
        print(f"Cached DataFrame saved to {cache_path}")
    print(f"Full quality pipeline executed in {elapsed_time:.2f} seconds for {dataset_size} rows.")

############################################################################################################

if evaluate_model:
    error_config = load_error_config()
    # -------------------------------------------------------------------------------------------------------------------
    # --- Helpers ---
    # -------------------------------------------------------------------------------------------------------------------

    def parse_errors(error_str):
        if error_str is None:
            return set()
        if isinstance(error_str, (set, list)):
            return set(error_str)
        if isinstance(error_str, np.ndarray):
            if error_str.size == 0:
                return set()
            return set(error_str.tolist())

        error_str = str(error_str).strip()
        if error_str in ["set()", "[]", "{}"]:
            return set()
        error_str = error_str.strip("{}[]").replace("'", "")
        return set(item.strip() for item in error_str.split(",") if item.strip())

    def combine_errors(row, columns):
            combined = set()
            for col in columns:
                combined |= parse_errors(row[col])
            return combined

    def count_errors(errors_set):
        error_counts = {}
        for error in errors_set:
            if error not in error_counts:
                error_counts[error] = 0
            error_counts[error] += 1
        return error_counts
    
    def filter_errors(error_set, mode='detect'):
        if mode == 'detect':
            return set(e for e in error_set if should_detect(str(e), error_config))
        elif mode == 'correct':
            return set(e for e in error_set if should_correct(str(e), error_config))
        return set()
    
    def count_statuses(series):
        return series.value_counts()
    
    def map_errors_to_dimensions(error_sets):
        dq_counter = Counter()
        for error_set in error_sets:
            for code in error_set:
                dq = dq_mapping.get(code)
                if dq:
                    dq_counter[dq] += 1
        return dq_counter
    
    def evaluate_performance(true_col, pred_col):
        accuracy = accuracy_score(true_col, pred_col)
        precision = precision_score(true_col, pred_col)
        recall = recall_score(true_col, pred_col)
        f1 = f1_score(true_col, pred_col)
        cm = confusion_matrix(true_col, pred_col)
        report = classification_report(true_col, pred_col, target_names=["No Error", "Error"])
        return accuracy, precision, recall, f1, cm, report

    # -------------------------------------------------------------------------------------------------------------------
    # --- Preprocessing ---
    # -------------------------------------------------------------------------------------------------------------------
    # Parse sets and combine errors
    df['INTRODUCED_ERRORS_SET'] = df['INTRODUCED_ERRORS'].apply(parse_errors)
    
    detected_cols = [col for col in df.columns if col.endswith('_DETECTED_ERRORS')]
    corrected_cols = [col for col in df.columns if col.endswith('_CORRECTED_ERRORS')]
    df['ALL_DETECTED_ERRORS'] = df.apply(lambda row: combine_errors(row, detected_cols), axis=1)
    df['ALL_CORRECTED_ERRORS'] = df.apply(lambda row: combine_errors(row, corrected_cols), axis=1)
    
    # Filter for only the errors that should be detected or corrected as per the config
    # df['INTRODUCED_ERRORS_SET_CONFIG_DETECT'] = df['INTRODUCED_ERRORS_SET'].apply(lambda s: filter_errors(s, 'detect'))
    # df['INTRODUCED_ERRORS_SET_CONFIG_CORRECT'] = df['INTRODUCED_ERRORS_SET'].apply(lambda s: filter_errors(s, 'correct'))

    # -------------------------------------------------------------------------------------------------------------------
    # --- Dataset stats ---
    # -------------------------------------------------------------------------------------------------------------------
    print("\n======================================================= Dataset stats =======================================================")
    # Dataset size and columns
    print(f"Dataset size: {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {', '.join(df.columns)}")
    # Count all rows with introduced errors
    df['HAS_INTRODUCED_ERRORS'] = df['INTRODUCED_ERRORS_SET'].apply(lambda x: len(x) > 0)
    num_rows_with_errors = df['HAS_INTRODUCED_ERRORS'].sum()
    print(f"Number of rows with introduced errors: {num_rows_with_errors} ({num_rows_with_errors / len(df) * 100:.2f}%)")
    # per filed count of rows with introduced errors
    for field in ["FIRST_NAME", "LAST_NAME", "STREET", "HOUSE_NUMBER",
                  "POSTAL_CODE", "POSTAL_CITY", "EMAIL", "PHONE_NUMBER"]:
        col_name = f"{field}_INTRO_ERRORS"
        num_rows_with_field_errors = df[col_name].apply(lambda x: len(parse_errors(x)) > 0).sum()
        print(f"Number of rows with introduced errors in {field}: {num_rows_with_field_errors} ({num_rows_with_field_errors / len(df) * 100:.2f}%)")
    
    # -------------------------------------------------------------------------------------------------------------------
    # --- Counting Errors ---
    # -------------------------------------------------------------------------------------------------------------------
    # Count errors in the introduced set
    df['ALL_DETECTED_ERRORS_COUNT'] = df['ALL_DETECTED_ERRORS'].apply(count_errors)
    df['ALL_CORRECTED_ERRORS_COUNT'] = df['ALL_CORRECTED_ERRORS'].apply(count_errors)
    df['INTRODUCED_ERRORS_COUNT'] = df['INTRODUCED_ERRORS_SET'].apply(count_errors)

    # Aggregate error counts
    detected_error_counts = Counter()
    df['ALL_DETECTED_ERRORS_COUNT'].apply(detected_error_counts.update)
    corrected_error_counts = Counter()
    df['ALL_CORRECTED_ERRORS_COUNT'].apply(corrected_error_counts.update)
    introduced_error_counts = Counter()
    df['INTRODUCED_ERRORS_COUNT'].apply(introduced_error_counts.update)

    error_comparison = pd.DataFrame({
        "Introduced": pd.Series(introduced_error_counts),
        "Detected": pd.Series(detected_error_counts),
        "Corrected": pd.Series(corrected_error_counts)
    }).fillna(0).astype(int)

    error_comparison["Detection Rate (%)"] = (error_comparison["Detected"] / error_comparison["Introduced"]) * 100
    error_comparison["Correction Rate (%)"] = (error_comparison["Corrected"] / error_comparison["Introduced"]) * 100
    error_comparison = error_comparison.round(2)
    
    print("\n======================================================= Errors Counts =======================================================")
    print(error_comparison.to_string(index=True))
    # save the table to file
    # error_comparison.to_csv('src/processed_data/error_comparison.csv', index=True)

    # ==================================================================================================
    # --- Error counts and row impact by FIELD (Introduced / Detected / Corrected) ----------------------
    # ==================================================================================================

    FIELDS = [
        "FIRST_NAME", "LAST_NAME", "STREET", "HOUSE_NUMBER",
        "POSTAL_CODE", "POSTAL_CITY", "EMAIL", "PHONE_NUMBER"
    ]

    results = []

    for field in FIELDS:
        intro_col     = f"{field}_INTRO_ERRORS"
        detect_col    = f"{field}_DETECTED_ERRORS"
        correct_col   = f"{field}_CORRECTED_ERRORS"

        # Parse all into sets
        intro_errors    = df[intro_col].apply(parse_errors)
        detected_errors = df[detect_col].apply(parse_errors)
        corrected_errors = df[correct_col].apply(parse_errors)

        # Count instances of error codes
        intro_count    = sum(len(x) for x in intro_errors)
        detected_count = sum(len(x) for x in detected_errors)
        corrected_count = sum(len(x) for x in corrected_errors)

        # Count rows affected
        intro_rows    = sum(len(x) > 0 for x in intro_errors)
        detected_rows = sum(len(x) > 0 for x in detected_errors)
        corrected_rows = sum(len(x) > 0 for x in corrected_errors)

        # Compute rates
        detection_rate = (detected_count / intro_count * 100) if intro_count else 0
        correction_rate = (corrected_count / intro_count * 100) if intro_count else 0

        results.append({
            "Field": field,
            "Introduced Errors": intro_count,
            "Detected Errors": detected_count,
            "Corrected Errors": corrected_count,
            "Detection Rate (%)": round(detection_rate, 2),
            "Correction Rate (%)": round(correction_rate, 2),
            "Rows with Introduced Errors": intro_rows,
            "Rows with Detected Errors": detected_rows,
            "Rows with Corrected Errors": corrected_rows
        })

    # Create DataFrame
    field_error_summary = pd.DataFrame(results)
    field_error_summary = field_error_summary.set_index("Field")

    # Display
    print("\n======================================================= ERROR COUNTS BY FIELD (TOTAL + ROW-LEVEL) =======================================================")
    print(field_error_summary.to_string())

    # Save to file
    # field_error_summary.to_csv("src/processed_data/field_error_summary.csv")

    # -------------------------------------------------------------------------------------------------------------------
    # --- Confussion matrix & Precision, recall & F1 score ---
    # -------------------------------------------------------------------------------------------------------------------
    
    print("\n======================================================= RECORD LEVEL =======================================================")
    
    print("\n======================================================= Level 1: Overall =======================================================")
    # check column introduced_errors and if its not empty then assig true to column has_intro_errors    
    df['HAS_INTRODUCED'] = df['INTRODUCED_ERRORS_SET'].apply(lambda x: len(x) > 0)
    df['HAS_DETECTED'] = df['ALL_DETECTED_ERRORS'].apply(lambda x: len(x) > 0)
    # df['HAS_CORRECTED'] = df['ALL_CORRECTED_ERRORS'].apply(lambda x: len(x) > 0)
    df['HAS_CORRECTED'] = df.apply(
        lambda row: row['ALL_CORRECTED_ERRORS'] == row['ALL_DETECTED_ERRORS'] and len(row['ALL_CORRECTED_ERRORS']) > 0,
        axis=1
    )
    
    true_col = df['HAS_INTRODUCED']
    pred_col_det = df['HAS_DETECTED']
    pred_col_corr = df['HAS_CORRECTED']
    
    # Check for detection
    print("\n==================================== DETECTION ====================================")
    accuracy, precision, recall, f1, cm, report = evaluate_performance(true_col, pred_col_det)
    print(f"Accuracy: {accuracy:.3f}; Precision: {precision:.3f}, Recall: {recall:.3f}, F1 Score: {f1:.3f}")
    print("Confusion Matrix:")
    print(cm)
    print("\nDetailed Classification Report:")
    print(report)
    
    # Check  for correction 
    print("\n==================================== CORRECTION ====================================")
    accuracy, precision, recall, f1, cm, report = evaluate_performance(true_col, pred_col_corr)
    print(f"Accuracy: {accuracy:.3f}; Precision: {precision:.3f}, Recall: {recall:.3f}, F1 Score: {f1:.3f}")
    print("Confusion Matrix:")
    print(cm)
    print("\nDetailed Classification Report:")
    print(report)
    
    # False-positive correction number and rate
    false_positive_corr = df[(df['HAS_INTRODUCED'] == False) & (df['HAS_CORRECTED'] == True)]
    false_positive_corr_count = len(false_positive_corr)
    false_positive_corr_rate = (false_positive_corr_count / len(df)) * 100 if len(df) > 0 else 0
    print(f"False Positive Corrections: {false_positive_corr_count} ({false_positive_corr_rate:.2f}%)")
    
    print("\n======================================================= Level 2: Error code =======================================================")
    # order the columns
    df['INTRODUCED_ERRORS_SET'] = df['INTRODUCED_ERRORS_SET'].apply(lambda x: sorted(x))
    df['INTRODUCED_ERRORS_SET'] = df['INTRODUCED_ERRORS_SET'].apply(lambda x: sorted(x))
    df['ALL_DETECTED_ERRORS'] = df['ALL_DETECTED_ERRORS'].apply(lambda x: sorted(x))
    df['ALL_CORRECTED_ERRORS'] = df['ALL_CORRECTED_ERRORS'].apply(lambda x: sorted(x))
    
    df['HAS_INTRODUCED_ERRORS_DETECT'] = df['INTRODUCED_ERRORS_SET'].apply(lambda x: len(x) > 0)
    df['HAS_INTRODUCED_ERRORS_CORRECT'] = df['INTRODUCED_ERRORS_SET'].apply(lambda x: len(x) > 0)
    
    df['HAS_DETECTED_ERRORS'] = df.apply(
        lambda row: False if (not row['ALL_DETECTED_ERRORS'] and not row['INTRODUCED_ERRORS_SET'])
        else row['ALL_DETECTED_ERRORS'] == row['INTRODUCED_ERRORS_SET'],
        axis=1
    )
    df['HAS_CORRECTED_ERRORS'] = df.apply(
        lambda row: False if (not row['ALL_CORRECTED_ERRORS'] and not row['INTRODUCED_ERRORS_SET'])
        else row['ALL_CORRECTED_ERRORS'] == row['INTRODUCED_ERRORS_SET'],
        axis=1
    )
    
    true_col_det = df['HAS_INTRODUCED_ERRORS_DETECT']
    true_col_corr = df['HAS_INTRODUCED_ERRORS_CORRECT']
    
    pred_col_det = df['HAS_DETECTED_ERRORS']
    pred_col_corr = df['HAS_CORRECTED_ERRORS']
    
    # Check for detection
    print("\n==================================== DETECTION ====================================")
    accuracy, precision, recall, f1, cm, report = evaluate_performance(true_col_det, pred_col_det)
    print(f"Accuracy: {accuracy:.3f}; Precision: {precision:.3f}, Recall: {recall:.3f}, F1 Score: {f1:.3f}")
    print("Confusion Matrix:")
    print(cm)
    print("\nDetailed Classification Report:")
    print(report)
    
    # Check  for correction 
    print("\n==================================== CORRECTION ====================================")
    accuracy, precision, recall, f1, cm, report = evaluate_performance(true_col_corr, pred_col_corr)
    print(f"Accuracy: {accuracy:.3f}; Precision: {precision:.3f}, Recall: {recall:.3f}, F1 Score: {f1:.3f}")
    print("Confusion Matrix:")
    print(cm)
    print("\nDetailed Classification Report:")
    print(report)    

    print("\n======================================================= ATTRIBUTE LEVEL =======================================================")

    ATTRIBUTES = [
        "FIRST_NAME", "LAST_NAME", "STREET", "HOUSE_NUMBER",
        "POSTAL_CODE", "POSTAL_CITY", "EMAIL", "PHONE_NUMBER"
    ]
    
    print("\n======================================================= Level 1: Overall =======================================================")
    for attr in ATTRIBUTES:
        print(f"\n---------- {attr} ----------")

        # check column introduced_errors and if its not empty then assig true to column has_intro_errors    
        df[f'{attr}_HAS_INTRODUCED'] = df[f'{attr}_INTRO_ERRORS'].apply(lambda x: len(x) > 0)
        df[f'{attr}_HAS_DETECTED'] = df[f'{attr}_DETECTED_ERRORS'].apply(lambda x: len(x) > 0)
        df[f'{attr}_HAS_CORRECTED'] = df.apply(
            lambda row: set(row[f'{attr}_CORRECTED_ERRORS']) == set(row[f'{attr}_DETECTED_ERRORS']) and len(set(row[f'{attr}_CORRECTED_ERRORS'])) > 0,
            axis=1
        )
        
        true_col = df[f'{attr}_HAS_INTRODUCED']
        pred_col_det = df[f'{attr}_HAS_DETECTED']
        pred_col_corr = df[f'{attr}_HAS_CORRECTED']
        
        # Detection metrics
        print("\n==================================== DETECTION ====================================")
        accuracy, precision, recall, f1, cm, report = evaluate_performance(true_col, pred_col_det)
        print(f"Accuracy: {accuracy:.3f}; Precision: {precision:.3f}, Recall: {recall:.3f}, F1 Score: {f1:.3f}")
        print("Confusion Matrix:")
        print(cm)
        print("\nDetailed Classification Report:")
        print(report)
        
        # Check  for correction 
        print("\n==================================== CORRECTION ====================================")
        accuracy, precision, recall, f1, cm, report = evaluate_performance(true_col, pred_col_corr)
        print(f"Accuracy: {accuracy:.3f}; Precision: {precision:.3f}, Recall: {recall:.3f}, F1 Score: {f1:.3f}")
        print("Confusion Matrix:")
        print(cm)
        print("\nDetailed Classification Report:")
        print(report)
        
    print("\n======================================================= Level 2: Error code =======================================================")
    for attr in ATTRIBUTES:
        print(f"\n---------- {attr} ----------")

        df['INTRODUCED_ERRORS_SET'] = df['INTRODUCED_ERRORS_SET'].apply(lambda x: sorted(x))
        df['INTRODUCED_ERRORS_SET'] = df['INTRODUCED_ERRORS_SET'].apply(lambda x: sorted(x))
        df[f'{attr}_DETECTED_ERRORS'] = df[f'{attr}_DETECTED_ERRORS'].apply(lambda x: sorted(x))
        df[f'{attr}_CORRECTED_ERRORS'] = df[f'{attr}_CORRECTED_ERRORS'].apply(lambda x: sorted(x))
        
        df['HAS_INTRODUCED_ERRORS_DETECT'] = df['INTRODUCED_ERRORS_SET'].apply(lambda x: len(x) > 0)
        df['HAS_INTRODUCED_ERRORS_CORRECT'] = df['INTRODUCED_ERRORS_SET'].apply(lambda x: len(x) > 0)
        
        df['HAS_DETECTED_ERRORS'] = df.apply(
            lambda row: False if (not row[f'{attr}_DETECTED_ERRORS'] and not row['INTRODUCED_ERRORS_SET'])
            else row[f'{attr}_DETECTED_ERRORS'] == row['INTRODUCED_ERRORS_SET'],
            axis=1
        )
        df['HAS_CORRECTED_ERRORS'] = df.apply(
            lambda row: False if (not row[f'{attr}_CORRECTED_ERRORS'] and not row['INTRODUCED_ERRORS_SET'])
            else row[f'{attr}_CORRECTED_ERRORS'] == row['INTRODUCED_ERRORS_SET'],
            axis=1
        )

        # Detection metrics
        true_col_det = df['HAS_INTRODUCED_ERRORS_DETECT']
        pred_col_det = df['HAS_DETECTED_ERRORS']

        print("\n[Detection]")
        accuracy, precision, recall, f1, cm, report = evaluate_performance(true_col_corr, pred_col_corr)
        print(f"Accuracy: {accuracy:.3f}; Precision: {precision:.3f}, Recall: {recall:.3f}, F1 Score: {f1:.3f}")
        print("Confusion Matrix:")
        print(cm)
        print("\nDetailed Classification Report:")
        print(report)   
        
        # Correction metrics
        true_col_corr = df['HAS_INTRODUCED_ERRORS_CORRECT']
        pred_col_corr = df['HAS_CORRECTED_ERRORS']
        
        print("\n[Correction]")
        accuracy, precision, recall, f1, cm, report = evaluate_performance(true_col_corr, pred_col_corr)
        print(f"Accuracy: {accuracy:.3f}; Precision: {precision:.3f}, Recall: {recall:.3f}, F1 Score: {f1:.3f}")
        print("Confusion Matrix:")
        print(cm)
        print("\nDetailed Classification Report:")
        print(report)   
    
    # -------------------------------------------------------------------------------------------------------------------
    # --- Counting Status ---
    # -------------------------------------------------------------------------------------------------------------------
    print("\n======================================================= Status Counts =======================================================")
    # Based on the final status of the row, provide counts of different statuses
    status_summary = pd.DataFrame()
    
    # status columns
    status_columns = [col for col in df.columns if col.endswith('_STATUS')]
    
    for col in status_columns:
        counts = count_statuses(df[col])
        counts.name = col
        status_summary = pd.concat([status_summary, counts], axis=1)

    # Compute status counts for each *_STATUS column
    status_counts_by_column = {col: count_statuses(df[col]) for col in status_columns}
    
    # Fill NaNs with 0 and convert to int
    status_summary = status_summary.fillna(0).astype(int)

    # Sort columns for clarity: OVERALL_STATUS first, then alphabetical
    cols_sorted = ['OVERALL_STATUS'] + sorted([c for c in status_summary.columns if c != 'OVERALL_STATUS'])
    status_summary = status_summary[cols_sorted] if 'OVERALL_STATUS' in status_summary.columns else status_summary

    # Display
    print(status_summary)
    
    # -------------------------------------------------------------------------------------------------------------------
    # --- DQ Dimension Improvements ---
    # -------------------------------------------------------------------------------------------------------------------
    print("\n======================================================= DQ Dimension Improvements =======================================================")
    # Convert error_config to DataFrame
    error_config_df = pd.DataFrame.from_dict(error_config, orient='index')
    error_config_df.index.name = 'error_code'
    error_config_df.reset_index(inplace=True)

    # Map error codes to DQ dimensions
    dq_mapping = {
        row["error_code"]: row["dq_dimension"]
        for _, row in error_config_df.iterrows()
        if pd.notna(row["dq_dimension"])
    }

    # Summarize introduced DQ problems (before cleaning)
    introduced_dq_counts = map_errors_to_dimensions(df['INTRODUCED_ERRORS_SET'])

    # Summarize corrected DQ problems (after cleaning)
    corrected_dq_counts = map_errors_to_dimensions(df['ALL_CORRECTED_ERRORS'])

    # Create summary DataFrame
    dq_summary = pd.DataFrame({
        "Introduced Errors": introduced_dq_counts,
        "Corrected Errors": corrected_dq_counts
    }).fillna(0)

    # Add correction rate
    dq_summary["Correction Rate (%)"] = (
        dq_summary["Corrected Errors"] / dq_summary["Introduced Errors"]
    ) * 100
    dq_summary = dq_summary.round(2)

    # Sort by correction rate or total introduced
    dq_summary = dq_summary.sort_values(by="Correction Rate (%)", ascending=False)
    print(dq_summary.to_string(index=True))


if generate_report:
    
    def escape_excel_formulas(df):
        return df.apply(lambda col: col.map(lambda x: f"'{x}" if isinstance(x, str) and x.startswith("=") else x))
    
    for col in df.columns:
            if "ERRORS" in col and df[col].dtype == "object":
                df[col] = df[col].apply(
                    lambda x: ", ".join(sorted(x)) if isinstance(x, (set, list)) else x
                )

    # Split the DataFrame into parts based on column prefixes
    overview_df = df[["CUSTOMER_ID", "FIRST_NAME_STATUS", "LAST_NAME_STATUS", "FULL_ADDRESS_STATUS",
                    "EMAIL_STATUS", "PHONE_NUMBER_STATUS", "OVERALL_STATUS"]]
    names_df = df[["CUSTOMER_ID"] + [col for col in df.columns if col.startswith(("FIRST_NAME", "LAST_NAME"))]]
    first_name_df = df[["CUSTOMER_ID"] + [col for col in df.columns if col.startswith(("FIRST_NAME"))]]
    last_name_df = df[["CUSTOMER_ID"] + [col for col in df.columns if col.startswith(("LAST_NAME"))]]
    address_df = df[["CUSTOMER_ID", "FULL_ADDRESS", "FULL_ADDRESS_VALID", "FULL_ADDRESS_CORRECTED"] 
                    + [col for col in df.columns if col.startswith(("STREET", "HOUSE_NUMBER", "POSTAL_CODE", "POSTAL_CITY"))]
                    + ["FULL_ADDRESS_VALID_AFTER_CORRECTION", "FULL_ADDRESS_STATUS"]]
    street_df = df[["CUSTOMER_ID", "FULL_ADDRESS", "FULL_ADDRESS_VALID", "FULL_ADDRESS_CORRECTED"] 
                    + [col for col in df.columns if col.startswith(("STREET"))]
                    + ["FULL_ADDRESS_VALID_AFTER_CORRECTION", "FULL_ADDRESS_STATUS"]]
    house_number_df = df[["CUSTOMER_ID", "FULL_ADDRESS", "FULL_ADDRESS_VALID", "FULL_ADDRESS_CORRECTED"] 
                    + [col for col in df.columns if col.startswith(("HOUSE_NUMBER"))]
                    + ["FULL_ADDRESS_VALID_AFTER_CORRECTION", "FULL_ADDRESS_STATUS"]]
    postal_code_df = df[["CUSTOMER_ID", "FULL_ADDRESS", "FULL_ADDRESS_VALID", "FULL_ADDRESS_CORRECTED"] 
                    + [col for col in df.columns if col.startswith(("POSTAL_CODE"))]
                    + ["FULL_ADDRESS_VALID_AFTER_CORRECTION", "FULL_ADDRESS_STATUS"]]
    postal_city_df = df[["CUSTOMER_ID", "FULL_ADDRESS", "FULL_ADDRESS_VALID", "FULL_ADDRESS_CORRECTED"] 
                    + [col for col in df.columns if col.startswith(("POSTAL_CITY"))]
                    + ["FULL_ADDRESS_VALID_AFTER_CORRECTION", "FULL_ADDRESS_STATUS"]]
    email_df = df[["CUSTOMER_ID"] + [col for col in df.columns if col.startswith("EMAIL")]]
    phone_df = df[["CUSTOMER_ID"] + [col for col in df.columns if col.startswith("PHONE_NUMBER")]]

    # Escape Excel formulas in the DataFrames
    overview_df = escape_excel_formulas(overview_df)
    names_df    = escape_excel_formulas(names_df)
    first_name_df = escape_excel_formulas(first_name_df)
    last_name_df = escape_excel_formulas(last_name_df)
    address_df  = escape_excel_formulas(address_df)
    street_df   = escape_excel_formulas(street_df)
    house_number_df = escape_excel_formulas(house_number_df)
    postal_code_df = escape_excel_formulas(postal_code_df)
    postal_city_df = escape_excel_formulas(postal_city_df)
    email_df    = escape_excel_formulas(email_df)
    phone_df    = escape_excel_formulas(phone_df)

    df.to_excel('src/processed_data/final_customer_data.xlsx', index=False)

    print(f"Processed data saved")