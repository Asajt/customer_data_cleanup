import pandas as pd
import re
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.errors_utils import should_correct, load_error_config

error_config = load_error_config()

def correct_address(street, street_number, zipcode, city, detected_errors):
    
    # Store the original address components for comparison purposes
    original_street = street
    original_street_number = street_number
    original_zipcode = zipcode
    original_city = city

    # Check for NaN values and convert them to empty strings
    street = "" if pd.isna(street) else str(street)
    street_number = "" if pd.isna(street_number) else str(street_number)
    zipcode = "" if pd.isna(zipcode) else str(zipcode)
    city = "" if pd.isna(city) else str(city)

    if isinstance(detected_errors, str):
        detected_errors = set(detected_errors.split(",")) if detected_errors else set()
    else:
        detected_errors = set()
        
    orig_detected_errors = detected_errors.copy() # Store the original detected errors for comparison
    corrected_errors = set()  # Set to store errors corrected during processing
    uncorrected_errors = set()  # Set to store errors that remain uncorrected