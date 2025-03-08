import pytest
import pandas as pd
from detection.detect_address import detect_address_errors

@pytest.fixture
def sample_data():
    """Create test cases where each row corresponds to a specific error code."""
    return pd.DataFrame({
        "STREET": ["", "  Main St  ", "123Main", "BŠ Road", "Valid Street"],
        "HOUSE_NUMBER": ["", "123", "BŠ", " 001", "A12"],
        "POSTAL_CODE": ["", "ABCDE", "123", "99999", "1000"],
        "POSTAL_CITY": ["", "Los Angeles ", "Paris123", "New York", "Valid City"]
    })

def test_error_101_missing_street(sample_data):
    """Test if error '101' is detected for missing street"""
    df = detect_address_errors(sample_data)
    assert "101" in df["DETECTED_STREET_ERRORS"][0]  # No information given

def test_error_102_extra_spaces(sample_data):
    """Test if error '102' is detected for unnecessary spaces"""
    df = detect_address_errors(sample_data)
    assert "102" in df["DETECTED_STREET_ERRORS"][1]  # Leading/trailing spaces

def test_error_110_street_starts_with_number(sample_data):
    """Test if error '110' is detected for streets that start with a digit"""
    df = detect_address_errors(sample_data)
    assert "110" in df["DETECTED_STREET_ERRORS"][2]  # Starts with a digit

def test_error_103_contains_BŠ(sample_data):
    """Test if error '103' is detected for 'BŠ' in street"""
    df = detect_address_errors(sample_data)
    assert "103" in df["DETECTED_STREET_ERRORS"][3]  # Contains 'BŠ'

def test_error_201_missing_house_number(sample_data):
    """Test if error '201' is detected for missing house number"""
    df = detect_address_errors(sample_data)
    assert "201" in df["DETECTED_HOUSE_NUMBER_ERRORS"][0]  # No house number

def test_error_206_leading_zero_house_number(sample_data):
    """Test if error '206' is detected for house number with leading zero"""
    df = detect_address_errors(sample_data)
    assert "206" in df["DETECTED_HOUSE_NUMBER_ERRORS"][3]  # Leading zero

def test_error_301_missing_postal_code(sample_data):
    """Test if error '301' is detected for missing postal code"""
    df = detect_address_errors(sample_data)
    assert "301" in df["DETECTED_POSTAL_CODE_ERRORS"][0]  # No postal code

def test_error_303_invalid_postal_code_characters(sample_data):
    """Test if error '303' is detected for postal codes with letters"""
    df = detect_address_errors(sample_data)
    assert "303" in df["DETECTED_POSTAL_CODE_ERRORS"][1]  # Contains letters

def test_error_305_less_than_4_digits_postal_code(sample_data):
    """Test if error '305' is detected for postal codes with less than 4 digits"""
    df = detect_address_errors(sample_data)
    assert "305" in df["DETECTED_POSTAL_CODE_ERRORS"][2]  # Less than 4 digits

def test_error_401_missing_city(sample_data):
    """Test if error '401' is detected for missing city"""
    df = detect_address_errors(sample_data)
    assert "401" in df["DETECTED_CITY_ERRORS"][0]  # No city information

def test_error_403_city_contains_digits(sample_data):
    """Test if error '403' is detected for city names with digits"""
    df = detect_address_errors(sample_data)
    assert "403" in df["DETECTED_CITY_ERRORS"][2]  # Contains numbers
