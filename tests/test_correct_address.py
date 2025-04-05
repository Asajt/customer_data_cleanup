import pytest
import pandas as pd
from correction.address_correction import correct_address_errors

@pytest.fixture
def sample_data():
    """Create test cases with errors that need correction."""
    return pd.DataFrame({
        "STREET": ["  Main St  ", "123Main", "BŠ Road", "Broadway..", None],
        "HOUSE_NUMBER": [" 001", "BŠ", " 123 ", None, "A12"],
        "POSTAL_CODE": [" 1000", "ABCDE", "123", "99999", None],
        "POSTAL_CITY": [" Los Angeles ", "Paris123", None, "New York", "Valid City"]
    })

def test_correct_street_spaces(sample_data):
    """Test if unnecessary spaces in street names are removed"""
    df = correct_address_errors(sample_data)
    assert df["CORRECTED_STREET"][0] == "Main St"

def test_correct_street_bš(sample_data):
    """Test if 'BŠ' is removed from street names"""
    df = correct_address_errors(sample_data)
    assert df["CORRECTED_STREET"][2] == "Road"

def test_correct_house_number_leading_zero(sample_data):
    """Test if leading zero in house number is removed"""
    df = correct_address_errors(sample_data)
    assert df["CORRECTED_HOUSE_NUMBER"][0] == "1"

def test_correct_postal_code_spaces(sample_data):
    """Test if postal code spaces are removed"""
    df = correct_address_errors(sample_data)
    assert df["CORRECTED_POSTAL_CODE"][0] == "1000"

def test_correct_postal_code_invalid_characters(sample_data):
    """Test if postal codes with letters are set to None"""
    df = correct_address_errors(sample_data)
    assert df["CORRECTED_POSTAL_CODE"][1] is None

def test_correct_city_spaces(sample_data):
    """Test if unnecessary spaces in city names are removed"""
    df = correct_address_errors(sample_data)
    assert df["CORRECTED_CITY"][0] == "Los Angeles"

def test_correct_city_invalid_numbers(sample_data):
    """Test if cities with digits are set to None"""
    df = correct_address_errors(sample_data)
    assert df["CORRECTED_CITY"][1] is None
