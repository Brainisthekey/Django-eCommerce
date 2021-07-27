from core.forms import CouponForm
from core.services.db_services import get_order_objects, get_coupon, check_user_for_active_coupon

def get_coupon_form_and_validate(request, form):
    """Get coupon form and validate date"""
    if form.is_valid():
        return form.cleaned_data
    return form.errors
    
#Проверить вообще где эту функции используются
def get_code_from_from(form):
    """Get code from form"""
    return form.cleaned_data.get('code')

#Проверить вообще где эту функции используются
def validate_from_for_whitespaces(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


