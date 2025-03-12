import pytest
import pandas as pd
from detection.detect_names import detect_name_errors  # Import your function

@pytest.mark.parametrize("name, surname, expected_errors", [
    # ✅ Missing Name Tests
    ("", "Smith", {"1101"}),
    (None, "Smith", {"1101"}),
    ("/", "Smith", {"1101"}),

    # ✅ Missing Surname Tests
    ("John", "", {"1201"}),
    ("John", None, {"1201"}),
    ("John", "/", {"1201"}),

    # ✅ Unnecessary Spaces
    (" John", "Smith", {"1102"}),  # Leading space
    ("John ", "Smith", {"1102"}),  # Trailing space
    ("John  Doe", "Smith", {"1102"}),  # Double space in name
    ("John", " Smith", {"1202"}),  # Leading space in surname
    ("John", "Smith ", {"1202"}),  # Trailing space in surname
    ("John", "Smith  Johnson", {"1202"}),  # Double space in surname

    # ✅ Invalid Characters
    ("J@hn", "Smith", {"1103"}),  # Special character in name
    ("John123", "Smith", {"1103"}),  # Number in name
    ("John", "Sm!th", {"1203"}),  # Special character in surname
    ("John", "Smith99", {"1203"}),  # Number in surname

    # ✅ Formatting Issues (not Title Case)
    ("john", "Smith", {"1104"}),  # Lowercase name
    ("JOHN", "Smith", {"1104"}),  # Uppercase name
    ("John", "smith", {"1204"}),  # Lowercase surname
    ("John", "SMITH", {"1204"}),  # Uppercase surname

    # ✅ Duplicates
    ("John John", "Smith", {"1105"}),  # Duplicate name
    ("John", "Smith Smith", {"1205"}),  # Duplicate surname

    # ✅ Valid Names (No Errors Expected)
    ("John", "Smith", set()),  # Properly formatted
    ("Jane Doe", "Johnson", set()),  # Multiple valid words
    ("O'Connor", "McDonald", set()),  # Special but valid cases
])
def test_detect_name_errors(name, surname, expected_errors):
    """Test detect_name_errors function for various inputs"""
    detected_errors = set(detect_name_errors(name, surname).split(",")) if detect_name_errors(name, surname) else set()
    assert detected_errors == expected_errors, f"Failed for ({name}, {surname})"

