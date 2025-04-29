import pandas as pd

# Load the dataset
data = pd.read_excel('/mnt/data/final_customer_data.xlsx')

# Helper to parse error strings into sets
def parse_errors(error_str):
    if pd.isna(error_str):
        return set()
    return set(str(error_str).replace(' ', '').split(','))

# Prepare columns
data['INTRODUCED_ERRORS_SET'] = data['INTRODUCED_ERRORS'].apply(parse_errors)
data['DETECTED_ERRORS_SET'] = data['PHONE_NUMBER_DETECTED_ERRORS'].apply(parse_errors)  # adjust if needed

# Calculate TP, FP, FN
def calculate_detection_metrics(row):
    introduced = row['INTRODUCED_ERRORS_SET']
    detected = row['DETECTED_ERRORS_SET']
    tp = len(introduced & detected)
    fp = len(detected - introduced)
    fn = len(introduced - detected)
    return pd.Series({'TP': tp, 'FP': fp, 'FN': fn})

metrics = data.apply(calculate_detection_metrics, axis=1)

# Summarize detection metrics
TP_total = metrics['TP'].sum()
FP_total = metrics['FP'].sum()
FN_total = metrics['FN'].sum()

precision = TP_total / (TP_total + FP_total) if (TP_total + FP_total) > 0 else 0
recall = TP_total / (TP_total + FN_total) if (TP_total + FN_total) > 0 else 0
f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

print("=== Error Detection Evaluation ===")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1 Score: {f1_score:.3f}")

# Overall record validation evaluation
expected_status = data['INTRODUCED_ERRORS_SET'].apply(lambda x: 'VALID' if len(x) == 0 else 'INVALID')
overall_accuracy = (data['OVERALL_STATUS'] == expected_status).mean()

print("\n=== Overall Record Status Evaluation ===")
print(f"Overall Status Accuracy: {overall_accuracy:.3f}")