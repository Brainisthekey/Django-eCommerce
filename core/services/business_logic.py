from core.services.db_services import get_order_item_title, get_order_quantity, get_all_objects_from_order_items


def delete_order_if_order_items_empty():
    if get_all_objects_from_order_items.count() == 0:
        pass


def get_information_about_order(orders):
    """Get infomation about order"""
    ordered_items = []
    ordered_quantity = 0
    for order in orders:
        ordered_items.append([order.quantity, order.item.title])
        ordered_quantity += order.quantity
    return ordered_quantity, ordered_items

def convert_order_items_into_string_view(orders):
    """Convert orders into string view"""
    string_filed = ''
    _, ordered_items = get_information_about_order(orders=orders)
    for i, item in enumerate(ordered_items, 1):
        fstring = f'{i}. {item[1]} x {item[0]} \n'
        string_filed += fstring
    return fstring.rstrip()

#Buiseness logic checkout view

from core.services.db_services import add_shipping_adress_to_the_order, change_status_default_address, create_a_new_address
from core.services.form_services import validate_from_for_whitespaces


#The logic for shiipping adress fileds and default shipping adress
def check_option_set_default(set_default_shipping, shipping_adress):
    """Save adress to default shipping adress"""
    if set_default_shipping:
        change_status_default_address(address=shipping_adress, status=True)


def validate_and_create_a_new_adress(
        user,
        order,
        set_default_shipping,
        shipping_address1,
        shipping_address2,
        shipping_country,
        shipping_zip
    ):
    """Validate form for whitespces and add shiping address to the order"""
    if validate_from_for_whitespaces([shipping_address1, shipping_country, shipping_zip]):
        shipping_adress = create_a_new_address(
            user=user,
            street_adress=shipping_address1,
            apartment_adress=shipping_address2,
            country=shipping_country,
            zip=shipping_zip,
            adress_type='S'
        )
        add_shipping_adress_to_the_order(order=order, adress_queryset=shipping_adress)
        check_option_set_default(set_default_shipping=set_default_shipping, shipping_adress=shipping_adress)
        return shipping_adress

def default_shipping_adress(
        user,
        order,
        use_default_shipping,
        address_shipping_queryset,
        set_default_shipping,
        shipping_address1,
        shipping_address2,
        shipping_country,
        shipping_zip
    ):
    """
        Add shiping adress to the order, if user enable option -
        'save as default' than add this adress to the Adress model
    """
    exist_default_shipping_adress = check_enabled_option_use_default_shipping(
        use_default_shipping=use_default_shipping,
        address_shipping_queryset=address_shipping_queryset,
        order=order
    )
    if exist_default_shipping_adress == "User do not have enabled option save as default":
        return validate_and_create_a_new_adress(
            user=user,
            order=order,
            set_default_shipping=set_default_shipping,
            shipping_address1=shipping_address1,
            shipping_address2=shipping_address2,
            shipping_country=shipping_country,
            shipping_zip=shipping_zip
        )
    elif exist_default_shipping_adress == 'Successfully added to the order':
        #See where we can use this message
        return 'User use the default shipping adress'
    return 'Please fill in the required shipping address fields'

    
def check_enabled_option_use_default_shipping(use_default_shipping, address_shipping_queryset, order):
    """Check if user has default shipping adress"""
    if use_default_shipping:
        check_default_shipping_adress(order=order, address_shipping_queryset=address_shipping_queryset)
    return "User do not have enabled option save as default"


def check_default_shipping_adress(order, address_shipping_queryset):
    """Check default shipping adress and if exist add to the order"""
    if address_shipping_queryset:
        add_shipping_adress_to_the_order(order=order, adress_queryset=address_shipping_queryset)
    return 'Successfully added to the order'


#Logic for the same billing adress as shipping with enabled and disabled option save