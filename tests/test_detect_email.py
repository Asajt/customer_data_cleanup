import pytest
from detection.email_detection import detect_email_errors

# Test 2101: missing or empty email
@pytest.mark.parametrize("email, expected_codes", [
    ("", {"2101"}),
    ("x", {"2101"}),
    ("   ", {"2101"}),
])
def test_missing_email(email, expected_codes):
    assert detect_email_errors(email) == expected_codes

# Test 2102: unnecessary spaces
@pytest.mark.parametrize("email, expected_codes", [
    (" test@email.com", {"2102"}),
    ("test@email.com ", {"2102"}),
    ("test@ email.com", {"2102"}),
])
def test_unnecessary_spaces(email, expected_codes):
    assert "2102" in detect_email_errors(email)

# Test 2103: invalid characters
@pytest.mark.parametrize("email, expected_codes", [
    ("te$st@email.com", {"2103"}),
    ("te!st@email.com", {"2103"}),
])
def test_invalid_characters(email, expected_codes):
    assert "2103" in detect_email_errors(email)

# Test 2104: formatting issues
@pytest.mark.parametrize("email, expected_codes", [
    ("testemail.com", {"2104"}),
    ("@test.com", {"2104"}),
    ("test@", {"2104"}),
    ("test@.com", {"2104"}),
])
def test_formatting_issues(email, expected_codes):
    assert "2104" in detect_email_errors(email)

# Test 2105: two emails in one field
@pytest.mark.parametrize("email, expected_codes", [
    ("test1@email.com, test2@email.com", {"2105"}),
    ("test1@email.com test2@email.com", {"2105"}),
])
def test_two_emails(email, expected_codes):
    assert "2105" in detect_email_errors(email)

# Test 2106: invalid domain structure
@pytest.mark.parametrize("email, expected_codes", [
    ("test@domain", {"2106"}),
    ("test@domain..com", {"2106"}),
])
def test_invalid_domain(email, expected_codes):
    assert "2106" in detect_email_errors(email)

# Test 2107: uncommon but valid domain
@pytest.mark.parametrize("email, expected_codes", [
    ("test@unknown123domain.com", {"2107"}),
])
def test_uncommon_domain(email, expected_codes):
    assert "2107" in detect_email_errors(email)

# Test 2000: fallback general invalid
@pytest.mark.parametrize("email, expected_codes", [
    ("test@.domain.com", {"2000"}),  # Should fail basic format validation
])
def test_general_invalid(email, expected_codes):
    assert "2000" in detect_email_errors(email)


'''
#### EMAIL

# email = 'x'

# rule_condition = email.strip() == "" or email.strip() == "x" or not re.search(r"[a-zA-Z0-9]", email)

################# 2103
email = 'x'
# Check for invalid characters (2103)
rule_condition = re.search(r"[^a-zA-Z0-9@_.+\-]", email)  # disallow anything not in the basic set
#################


'''