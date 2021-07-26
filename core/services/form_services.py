from core.forms import CouponForm
from core.services.db_services import get_order_objects, get_coupon, check_user_for_active_coupon

def get_coupon_form_and_validate(request, form):
    """Get coupon form and validate date"""
    if form.is_valid():
        return form.cleaned_data
    return form.errors
    

def get_code_from_from(form):
    """Get code from form"""
    return form.cleaned_data.get('code')