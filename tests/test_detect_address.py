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



'''


hn_patterns = ['BŠ', 'B.Š.', 'B. ŠT.', 'B.ŠT.', 'B$', 'BREZ ŠT.', 'BS', 'B.S.', 'NH', 'N.H.', 'BH', 'B.H.']

roman_numbers = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'
                , 'XI', 'XII', 'XIII', 'XIV','XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX'
                , 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII', 'XXVIII', 'XXIX', 'XXX'
                , 'XXXI'
                , 'XL']
allowed_abbreviations_street = ['dr', 'Sv', 'Vel']
allowed_abbreviations_street.extend(roman_numbers)

street1 = 'Barletova ce.  B$'
street11 = 'Zagrebška ulica'
street2 = '1.maja 215'
street3 = '.'

zipcode_errors = '4303'
# zipcode_errors = ''

# zipcode = '-400'
# zipcode = 'abs'
zipcode = '400'
street_number = 'V 5'
street_number = 'HŠ 5'

# rule_condition = any(re.search(re.escape(pattern), street1, re.IGNORECASE) for pattern in hn_patterns)    

# rule_condition = any(
#     re.search(r'(?<!\w)' + re.escape(pattern) + r'(?!\w)', street1, re.IGNORECASE)
#     for pattern in hn_patterns)

# rule_condition = street2 and re.search(r'\.(?![\s\W])',street2)

# Allow only: letters, numbers, spaces, dots, commas, slashes, hyphens
# rule_condition = not re.search(r'^[a-zA-ZčćšžČĆŠŽ\d\s\.,-/]+$', street3) or \
#                 '//' in street3 or \
#                 not re.search(r"[a-zA-ZčćšžČĆŠŽ0-9]", street3) #cannot have only special characters
                
# 4304 Check for less than 4 digits
# rule_condition = re.search(r"\d{1,3}$", zipcode)

rule_condition = re.search(r'^[^0-9]', street_number) and \
    not re.search(r'^\s', street_number) and \
    not any(re.match(rf"^{re.escape(p)}", street_number) for p in roman_numbers + hn_patterns)

# skip_if_condition = not '4303' in zipcode_errors
# rule_condition = re.search(r"^\d{1,3}$", zipcode)
# if skip_if_condition:





##################### formatting issues in street


street = 'pOd HruseVCO' #trigger
street = 'Gub=eva cesta' #dont trigger
street = 'Cesta 19. oktobra ' #dont trigger
# street = 'Rabel^ja vas '
# street = 'Ulica  bratov U!akar'
# street = '.'
street = 'Ulica  Franca Rozmana-Staneta'
# street = 'Ciril-Metodov trg'
street = 'ULICA  PRVOBORCEV N.H.'
# street = 'Ulica VIII'
street = ' Spodnji Rudnik II 627'
# 


pattern = r'(?<!\w)(' + '|'.join([re.escape(pat) for pat in hn_patterns+roman_numbers]) + r')(?!\w)'
cleaned_street = re.sub(pattern, '', street, flags=re.IGNORECASE).strip()
cleaned_street = re.sub(r"[^a-zA-ZčćšžČĆŠŽ\s]", " ", cleaned_street.strip(), flags=re.IGNORECASE)
words = cleaned_street.strip().split()
rule_condition = bool(words) and ( # this ensures that if the string must containt at least one lettter to be evaluated 
    not words[0].istitle() or #the frist word has to be in title case
    any(not (word.islower() or word.istitle()) for word in words[1:]) # all other words can either be in title case or all lower case
    )
# if rule_condition:


# if rule_condition0 and not rule_condition_4106:

#####################


####################### 4107: invalid abbreviations
street = 'Šaleška B.Š.'
street = 'Šaleška ce. B$'

street = 'Mesarska c. B.S.'
street = 'Sitarjevška cesta B.Š.'
street = 'Seskova ulica B.S.'
# street = 'Cankarjeva u. NH'
street = 'Pot k čuvajnici B.Š.'
# street = 'Oljøna pot B.Š.'
street = 'Ulica I.brigade VDV B.S.'

# remove all hn patterns from the string
pattern = r'(?<!\w)(' + '|'.join([re.escape(pat) for pat in hn_patterns+roman_numbers]) + r')(?!\w)'
cleaned_street = re.sub(pattern, '', street, flags=re.IGNORECASE).strip()
# print(cleaned_street)
rule_condition = re.search(r'(?<!\d)\.',cleaned_street) and \
                re.search(r'\b(?!(?:' + '|'.join(allowed_abbreviations_street) + r')\.)\w+\.', street, flags=re.IGNORECASE)



################# 4103

street = 'x'
rule_condition = (not re.search(r'^[a-zA-ZčćšžČĆŠŽ\d\s\.,-/]+$', street) or
    '//' in street or
    not re.search(r"[a-zA-ZčćšžČĆŠŽ0-9]", street) or #cannot have only special characters
    len(street.strip()) <= 1) # cannot be only one character
rule_condition_4106 = any(
    re.search(r'(?<!\w)' + re.escape(pattern) + r'(?!\w)', street, re.IGNORECASE)
    for pattern in hn_patterns)
# if rule_condition:# and not rule_condition_4106:

#################

#################



######## MAIN ############
if rule_condition:
    print("error")
else:
    print("ok")
    
    
    
'''