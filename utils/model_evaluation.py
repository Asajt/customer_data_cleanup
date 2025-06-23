import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.errors_utils import should_detect, load_error_config, should_correct
from collections import Counter

# Load error configuration and data
error_config = load_error_config()
data = pd.read_excel('./src/processed_data/final_customer_data.xlsx')

# -------------------------------------------------------------------------------------------------------------------
# --- Helpers ---
# -------------------------------------------------------------------------------------------------------------------
def filter_errors(error_set, mode='detect'):
    if mode == 'detect':
        return set(e for e in error_set if should_detect(str(e), error_config))
    elif mode == 'correct':
        return set(e for e in error_set if should_correct(str(e), error_config))
    return set()

def parse_errors(error_str):
    if pd.isna(error_str) or str(error_str).strip() in ["set()", "[]", "{}"]:
        return set()
    error_str = str(error_str).strip()
    if error_str.startswith("{") or error_str.startswith("["):
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

# -------------------------------------------------------------------------------------------------------------------
# --- Preprocessing ---
# -------------------------------------------------------------------------------------------------------------------
# Parse sets
data['INTRODUCED_ERRORS_SET'] = data['INTRODUCED_ERRORS'].apply(parse_errors)

# Filter for only the errors that should be detected or corrected as per the config
data['INTRODUCED_ERRORS_SET_DETECT'] = data['INTRODUCED_ERRORS_SET'].apply(lambda s: filter_errors(s, 'detect'))
data['INTRODUCED_ERRORS_SET_CORRECT'] = data['INTRODUCED_ERRORS_SET'].apply(lambda s: filter_errors(s, 'correct'))

# Relevant columns
detected_cols = [col for col in data.columns if col.endswith('_DETECTED_ERRORS')]
corrected_cols = [col for col in data.columns if col.endswith('_CORRECTED_ERRORS')]

# Combine detected and corrected error sets

data['ALL_DETECTED_ERRORS'] = data.apply(lambda row: combine_errors(row, detected_cols), axis=1)
data['ALL_CORRECTED_ERRORS'] = data.apply(lambda row: combine_errors(row, corrected_cols), axis=1)

# -------------------------------------------------------------------------------------------------------------------
# --- Counting Errors ---
# -------------------------------------------------------------------------------------------------------------------
# Based on the column ALL_DETECTED_ERRORS provide general stats on detected errors per error code in the whole dataset
def count_errors(errors_set):
    error_counts = {}
    for error in errors_set:
        if error not in error_counts:
            error_counts[error] = 0
        error_counts[error] += 1
    return error_counts

# Count all detected and corrected errors
data['ALL_DETECTED_ERRORS_COUNT'] = data['ALL_DETECTED_ERRORS'].apply(count_errors)
data['ALL_CORRECTED_ERRORS_COUNT'] = data['ALL_CORRECTED_ERRORS'].apply(count_errors)

# Aggregate error counts
detected_error_counts = Counter()
data['ALL_DETECTED_ERRORS_COUNT'].apply(detected_error_counts.update)

corrected_error_counts = Counter()
data['ALL_CORRECTED_ERRORS_COUNT'].apply(corrected_error_counts.update)

print("=== Detected Errors Counts ===")
for error, count in detected_error_counts.items():
    print(f"{error}: {count}")

# -------------------------------------------------------------------------------------------------------------------
# --- Counting Status ---
# -------------------------------------------------------------------------------------------------------------------
# Based on the final status of the row, provide counts of different statuses
def count_statuses(series):
    return series.value_counts().to_dict()

# Overall status counts
overall_status_counts = count_statuses(data['OVERALL_STATUS'])

# Identify all *_STATUS columns except OVERALL_STATUS
status_columns = [col for col in data.columns if col.endswith('_STATUS') and col != 'OVERALL_STATUS']

# Compute status counts for each *_STATUS column
status_counts_by_column = {
    col: count_statuses(data[col]) for col in status_columns
}

print("=== Overall Status Counts ===")
for status, count in overall_status_counts.items():
    print(f"{status}: {count}")

print("\n=== Per-Column Status Counts ===")
for col, status_dict in status_counts_by_column.items():
    print(f"\n{col}:")
    for status, count in status_dict.items():
        print(f"  {status}: {count}")

# -------------------------------------------------------------------------------------------------------------------
# --- Confussion matrix ---
# -------------------------------------------------------------------------------------------------------------------
# Compute TP, FP, FN from actual set comparison
def evaluate(actual, predicted):
    tp = len(actual & predicted)
    fp = len(predicted - actual)
    fn = len(actual - predicted)
    return tp, fp, fn

# Detection evaluation
det_results = data.apply(lambda row: evaluate(row['INTRODUCED_ERRORS_SET_DETECT'], row['ALL_DETECTED_ERRORS']), axis=1)
det_df = pd.DataFrame(det_results.tolist(), columns=['TP', 'FP', 'FN'])

# Correction evaluation
cor_results = data.apply(lambda row: evaluate(row['INTRODUCED_ERRORS_SET_CORRECT'], row['ALL_CORRECTED_ERRORS']), axis=1)
cor_df = pd.DataFrame(cor_results.tolist(), columns=['TP', 'FP', 'FN'])

# -------------------------------------------------------------------------------------------------------------------
# --- Precision, recall & F1 score ---
# -------------------------------------------------------------------------------------------------------------------
def summarize(df):
    TP, FP, FN = df[['TP', 'FP', 'FN']].sum()
    precision = TP / (TP + FP) if (TP + FP) else 0
    recall = TP / (TP + FN) if (TP + FN) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    return precision, recall, f1

det_precision, det_recall, det_f1 = summarize(det_df)
cor_precision, cor_recall, cor_f1 = summarize(cor_df)

# Output results
print("=== Detection Evaluation ===")
print(f"Precision: {det_precision:.3f}")
print(f"Recall:    {det_recall:.3f}")
print(f"F1 Score:  {det_f1:.3f}")

print("\n=== Correction Evaluation ===")
print(f"Precision: {cor_precision:.3f}")
print(f"Recall:    {cor_recall:.3f}")
print(f"F1 Score:  {cor_f1:.3f}")