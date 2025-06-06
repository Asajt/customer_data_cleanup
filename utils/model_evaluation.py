import pandas as pd

# Load the dataset
data = pd.read_excel('./src/processed_data/final_customer_data.xlsx')



# --- Helpers ---
def parse_errors(error_str):
    if pd.isna(error_str) or str(error_str).strip() in ["set()", "[]", "{}"]:
        return set()
    error_str = str(error_str).strip()
    if error_str.startswith("{") or error_str.startswith("["):
        error_str = error_str.strip("{}[]").replace("'", "")
    return set(item.strip() for item in error_str.split(",") if item.strip())

# Parse sets
data['INTRODUCED_ERRORS_SET'] = data['INTRODUCED_ERRORS'].apply(parse_errors)

# Relevant columns
detected_cols = [col for col in data.columns if col.endswith('_DETECTED_ERRORS')]
corrected_cols = [col for col in data.columns if col.endswith('_CORRECTED_ERRORS')]

# Combine detected and corrected error sets
def combine_errors(row, columns):
    combined = set()
    for col in columns:
        combined |= parse_errors(row[col])
    return combined

data['ALL_DETECTED_ERRORS'] = data.apply(lambda row: combine_errors(row, detected_cols), axis=1)
data['ALL_CORRECTED_ERRORS'] = data.apply(lambda row: combine_errors(row, corrected_cols), axis=1)

# Compute TP, FP, FN from actual set comparison
def evaluate(actual, predicted):
    tp = len(actual & predicted)           # Correctly found errors
    fp = len(predicted - actual)           # Incorrectly flagged/corrected
    fn = len(actual - predicted)           # Missed errors
    return tp, fp, fn

# Detection evaluation
det_results = data.apply(lambda row: evaluate(row['INTRODUCED_ERRORS_SET'], row['ALL_DETECTED_ERRORS']), axis=1)
det_df = pd.DataFrame(det_results.tolist(), columns=['TP', 'FP', 'FN'])

# Correction evaluation
cor_results = data.apply(lambda row: evaluate(row['INTRODUCED_ERRORS_SET'], row['ALL_CORRECTED_ERRORS']), axis=1)
cor_df = pd.DataFrame(cor_results.tolist(), columns=['TP', 'FP', 'FN'])

# Metric summarization
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

# Optional: Overall status accuracy
expected_status = data['INTRODUCED_ERRORS_SET'].apply(lambda x: 'VALID' if not x else 'INVALID')
actual_status = data['OVERALL_STATUS'].replace('PARTIALLY_VALID', 'INVALID')
accuracy = (expected_status == actual_status).mean()

print("\n=== Overall Status Accuracy ===")
print(f"Accuracy: {accuracy:.3f}")
