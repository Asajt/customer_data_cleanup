import regex as re

name = 'Ížtók'
# name = 'Iztok'
# 1103 Check for invalid characters
# skip_if_condition = not '1107' in name_errors
rule_condition = (not re.search(r'^[a-zčćšžđ\s]+$', name, re.IGNORECASE))
# if should_detect('1103', error_config):
    # if skip_if_condition:
    #     if rule_condition:
    #         name_errors.add('1103')

if rule_condition:
    print("Error detected")
else:
    print("No error detected")

'''
# 1104 Check for formatting issues
skip_if_condition = not '1106' in name_errors
cleaned_name = re.sub(r"[^a-zA-ZčćšžđČĆŠŽĐ\s]", "", name.strip(), flags=re.IGNORECASE)
rule_condition = (not cleaned_name.istitle())
if should_detect('1104', error_config):
    if skip_if_condition:
        if rule_condition:
            name_errors.add('1104')
'''