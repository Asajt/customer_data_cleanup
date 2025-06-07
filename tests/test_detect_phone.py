import pytest
from detection.phone_detection import detect_phone_errors

# Test 3101: Missing or placeholder phone number
@pytest.mark.parametrize("phone, expected", [
    ("", {"3101"}),
    ("x", {"3101"}),
    ("   ", {"3101"}),
])
def test_missing_phone(phone, expected):
    assert detect_phone_errors(phone) == expected

# Test 3102: Unnecessary spaces
@pytest.mark.parametrize("phone", [
    (" 00386123456789"),
    ("00386123456789 "),
    ("00386 123456789"),
])
def test_unnecessary_spaces(phone):
    assert "3102" in detect_phone_errors(phone)

# Test 3107: Multiple phone numbers
@pytest.mark.parametrize("phone", [
    ("00386123456789,00386111222333"),
    ("00386123456789 00386111222333"),
    ("00386123456789;00386111222333"),
])
def test_multiple_phone_numbers(phone):
    assert "3107" in detect_phone_errors(phone)

# Test 3103: Invalid characters
@pytest.mark.parametrize("phone", [
    ("00386abc1234"),
    ("00386-123456"),
])
def test_invalid_characters(phone):
    assert "3103" in detect_phone_errors(phone)

# Test 3105: Too many digits
@pytest.mark.parametrize("phone", [
    ("0038612345678911"),  # 14 digits
])
def test_too_many_digits(phone):
    assert "3105" in detect_phone_errors(phone)

# Test 3106: Too few digits
@pytest.mark.parametrize("phone", [
    ("00386123"),  # too short
])
def test_too_few_digits(phone):
    assert "3106" in detect_phone_errors(phone)

# Test 3104: Formatting issue
@pytest.mark.parametrize("phone", [
    ("+386123456789"),
    ("0386123456789"),
    ("86123456789"),
])
def test_formatting_issue(phone):
    assert "3104" in detect_phone_errors(phone)
    
    
    
'''

################# 3105
phone = '+00386707696169 '
rule_condition = len(re.findall(r"\d", phone)) > 13

################# 3103
phone = '0038664494841 '
phone = ' OO3864O8O7I25'
phone = '064 946 '
rule_condition = not phone.replace(" ", "").isdigit()


################# 3107 Check for two phone numbers
phone = '064/498/706, 0038631357874'
rule_condition = len(re.findall(r"\d{6,}", phone)) > 1

'''