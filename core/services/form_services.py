from core.forms import CouponForm
from core.services.db_services import get_order_objects, get_coupon, check_user_for_active_coupon


#Проверить вообще где эту функции используются
def validate_from_for_whitespaces(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


