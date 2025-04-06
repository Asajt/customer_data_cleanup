import regex as re

street = ''
original_street = street
corrected_street = street

detected_street_errors = {'4105', '4103'}
corrected_street_errors = set()  
uncorrected_street_errors = detected_street_errors.copy()

if detected_street_errors:
        if '4102' in detected_street_errors: # Street error: unnecessary spaces
            corrected_street_before = corrected_street
            corrected_street = corrected_street.rstrip() # removes trailing whitespaces
            corrected_street = corrected_street.lstrip() # removes leading whitespaces
            corrected_street = re.sub(r'\s{2,}', ' ', corrected_street) # removes double whitespace
            corrected_street = re.sub(r'\s,', ',', corrected_street) # removes whitespaces before comma
            if corrected_street_before != corrected_street:
                corrected_street_errors.add('4102')
                uncorrected_street_errors.remove('4102')
                
if corrected_street != original_street:
    street = corrected_street 
else:
    street = None
    
    
print(street)
print(detected_street_errors)
print(corrected_street)
print(uncorrected_street_errors)