import pytest

# Import validation functions
import os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
from validation.names_validation import validate_names
from validation.phone_validation import validate_phone
from validation.email_validation import validate_email
from validation.address_validation import validate_full_address

# === NAME VALIDATION ===
def test_valid_names():
    assert validate_names("Ana", "Novak") is True

def test_invalid_names():
    assert validate_names("ana", "novak") is False  # Assuming capitalization is required

# === PHONE VALIDATION ===
def test_valid_phone():
    assert validate_phone("0038631123456") is True

def test_invalid_phone_short():
    assert validate_phone("00386") is False

def test_invalid_phone_wrong_prefix():
    assert validate_phone("031123456") is False

# === EMAIL VALIDATION ===
def test_valid_email():
    assert validate_email("test.user@gmail.com") is True

def test_invalid_email_format():
    assert validate_email("test@com") is False

def test_invalid_email_missing_at():
    assert validate_email("test.gmail.com") is False

# === ADDRESS VALIDATION ===
def test_valid_address():
    reference_addresses = {"Trubarjeva ulica 7, Ljubljana"}
    assert validate_full_address("Trubarjeva ulica 7, Ljubljana", reference_addresses) is True

def test_invalid_address_not_in_ref():
    reference_addresses = {"Cankarjeva 5, Maribor"}
    assert validate_full_address("Fake Street 1, Nowhere", reference_addresses) is False
