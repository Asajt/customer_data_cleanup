import pytest
from detection.names_detection import detect_name_errors

# === HELPERS ===
def get_name_errors(name, surname=""):
    return detect_name_errors(name, surname)[0]

def get_surname_errors(name="", surname=""):
    return detect_name_errors(name, surname)[1]

# === NAME TESTS ===

# 1101: Missing name
@pytest.mark.parametrize("name", ["", "x", "     "])
def test_name_missing(name):
    errors = get_name_errors(name)
    assert "1101" in errors

# 1102: Unnecessary spaces
@pytest.mark.parametrize("name", [" Marko", "Marko ", "Marko  Novak"])
def test_name_spaces(name):
    errors = get_name_errors(name)
    assert "1102" in errors

# 1103: Invalid characters
@pytest.mark.parametrize("name", ["Mo3jc@", "An@", "Ž@n@", "M0nc!ca"])
def test_name_invalid_characters(name):
    errors = get_name_errors(name)
    assert "1103" in errors

# 1104: Formatting issues (not title case)
@pytest.mark.parametrize("name", ["marko", "MARKO", "marKo", "mARko"])
def test_name_formatting(name):
    errors = get_name_errors(name)
    assert "1104" in errors

# 1105: Duplicate names
def test_name_duplicates():
    errors = get_name_errors("Marko in Marko")
    assert "1105" in errors

# 1106: Two names in one field
@pytest.mark.parametrize("name", ["Ana in Meta", "Ana, Meta"])
def test_name_two_names(name):
    errors = get_name_errors(name)
    assert "1106" in errors

# 1107: Initials present
@pytest.mark.parametrize("name", ["O. Marija", "J."])
def test_name_initials(name):
    errors = get_name_errors(name)
    assert "1107" in errors

# === SURNAME TESTS ===

# 1201: Missing surname
@pytest.mark.parametrize("surname", ["", "x", "   "])
def test_surname_missing(surname):
    errors = get_surname_errors(surname=surname)
    assert "1201" in errors

# 1202: Unnecessary spaces
@pytest.mark.parametrize("surname", [" Novak", "Novak ", "Novak  Novak"])
def test_surname_spaces(surname):
    errors = get_surname_errors(surname=surname)
    assert "1202" in errors

# 1203: Invalid characters
@pytest.mark.parametrize("surname", ["Sn3ž@n@", "Ža#n"])
def test_surname_invalid_characters(surname):
    errors = get_surname_errors(surname=surname)
    assert "1203" in errors

# 1204: Formatting issues (not title case)
@pytest.mark.parametrize("surname", ["novak", "NOVAK", "noVAK"])
def test_surname_formatting(surname):
    errors = get_surname_errors(surname=surname)
    assert "1204" in errors

# 1205: Duplicate surnames
def test_surname_duplicates():
    errors = get_surname_errors(surname="Novak Novak")
    assert "1205" in errors


'''

################# 1104
# 1104 Check for formatting issues
name = 'M0jc@'
name = 'EL1Z@B3T@'
name = 'Sn3ž@n@'
name = 'D1mch3 M0jc'

cleaned_name = re.sub(r"[^a-zA-ZčćšžČĆŠŽ\s]", "", name.strip(), flags=re.IGNORECASE)
rule_condition = (not cleaned_name.istitle())

################# 1107

name = 'O. Marija'

# 1107 Initials present
# rule_condition = any(re.fullmatch(r"[A-ZČĆŠŽ]{1}\.?", word) for word in name.split())
rule_condition = any(re.fullmatch(r"[A-ZČĆŠŽ]{1}\.?", word.strip()) for word in name.strip().split())

################# 110 duplicates
name = 'Marko in Marko'

names = name.split()
counts = {}
for i in names:
    if i not in counts:
        counts[i] = 0
    counts[i] += 1
rule_condition = (any(count > 1 for count in counts.values()))

'''