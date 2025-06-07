import pytest
from detection.address_detection import detect_address_errors

# === HELPERS ===
def extract_street_errors(street, number="", zip="", city=""):
    return detect_address_errors(street, number, zip, city)[0]

def extract_number_errors(street="", number="", zip="", city=""):
    return detect_address_errors(street, number, zip, city)[1]

def extract_zipcode_errors(street="", number="", zip="", city=""):
    return detect_address_errors(street, number, zip, city)[2]

def extract_city_errors(street="", number="", zip="", city=""):
    return detect_address_errors(street, number, zip, city)[3]

# === STREET TESTS ===

# 4103: Invalid characters in street
@pytest.mark.parametrize("street", ["x", "!!", ".", "//"])
def test_invalid_street_format(street):
    errors = extract_street_errors(street)
    assert "4103" in errors

# 4106: Street contains house number patterns
@pytest.mark.parametrize("street", [
    "Ulica  PRVOBORCEV N.H.",
    "Sitarjevška cesta B.Š.",
    "Pot k čuvajnici B.S.",
])
def test_house_number_patterns_in_street(street):
    errors = extract_street_errors(street)
    assert "4106" in errors

# 4107: Invalid abbreviations
@pytest.mark.parametrize("street", [
    "Šaleška ce. B$",
    "Ulica I.brigade VDV B.S.",
])
def test_invalid_street_abbreviations(street):
    errors = extract_street_errors(street)
    assert "4107" in errors

# 4101: Missing or very short street
def test_street_missing_or_too_short():
    assert "4101" in extract_street_errors("")
    assert "4101" in extract_street_errors("A")

# 4104: Improper formatting (casing)
def test_street_formatting_casing():
    assert "4104" in extract_street_errors("pOd HruseVCO")

# === STREET NUMBER TESTS ===

# 4201: Missing street number
def test_street_number_missing():
    assert "4201" in extract_number_errors(number="")

# 4211: Street number does not start with digit
def test_street_number_non_digit_start():
    assert "4211" in extract_number_errors(number="HŠ 5")

# === ZIP CODE TESTS ===

# 4303: Invalid characters in ZIP
def test_zipcode_invalid_chars():
    assert "4303" in extract_zipcode_errors(zip="abs")

# 4304: ZIP too short
def test_zipcode_too_short():
    assert "4304" in extract_zipcode_errors(zip="123")

# === CITY TESTS ===

# 4405: City contains digits
def test_city_with_digit():
    assert "4405" in extract_city_errors(city="Ljubljana1")

# 4401: Missing city
def test_city_missing():
    assert "4401" in extract_city_errors(city="")
