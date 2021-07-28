
#Thif file represents the buiseness logic of forms
def validate_from_for_whitespaces(values):
    """Form validation for whitespaces"""
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


