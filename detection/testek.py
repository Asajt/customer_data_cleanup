import re 

hn_patterns = ['BŠ', 'B.Š.', 'B. ŠT.', 'B.ŠT.', 'B$', 'BREZ ŠT.', 'BS', 'B.S.', 'NH', 'N.H.', 'BH', 'B.H.']

roman_numbers = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'
                , 'XI', 'XII', 'XIII', 'XIV','XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX'
                , 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII', 'XXVIII', 'XXIX', 'XXX'
                , 'XXXI'
                , 'XL']

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


#### EMAIL

email = 'x'

rule_condition = email.strip() == "" or email.strip() == "x" or not re.search(r"[a-zA-Z0-9]", email)
if rule_condition:
        print("error")
else:
    print("ok")
    
    
    
