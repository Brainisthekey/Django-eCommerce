from core.services.db_services import (
    create_a_new_address,
    add_billing_address_to_the_order,
    change_status_default_address,
    add_shipping_adress_to_the_order,
    get_all_objects_from_order_items,
    check_adress_by_street_adress,
    filter_and_check_default_adress,
    create_a_new_devilered_order_object,
    delete_all_items_from_order,
    delete_order,
)
from core.services.form_services import validate_from_for_whitespaces

# General logic
def get_information_about_order(orders):
    """
    Get infomation about order
    Get title and quantity of order
    """
    ordered_items = []
    ordered_quantity = 0
    for order in orders:
        ordered_items.append([order.quantity, order.item.title])
        ordered_quantity += order.quantity
    return ordered_quantity, ordered_items


def convert_order_items_into_string_view(orders):
    """Convert orders into string representation"""
    string_filed = ""
    _, ordered_items = get_information_about_order(orders=orders)
    for i, item in enumerate(ordered_items, 1):
        fstring = f"{i}. {item[1]} x {item[0]} \n"
        string_filed += fstring
    return fstring.rstrip()


# Buiseness logic checkout view


def check_option_set_default(set_default_shipping, shipping_adress, user, adress_type):
    """
    Check option - Save as default shipping address
    if enabled option and user has default adress:
        Change status previosly default adress and set a new
        Set up a new default shipping address
    if disabled option:
        Set up a new default shipping address
    """
    address_queryset = filter_and_check_default_adress(
        user=user,
        adress_type=adress_type,
    )
    if set_default_shipping:
        if address_queryset:
            return change_status_default_address(address_queryset, status=False)
    return change_status_default_address(address=shipping_adress, status=True)


def validate_and_create_a_new_adress(
    user,
    order,
    set_default_shipping,
    shipping_address1,
    shipping_address2,
    shipping_country,
    shipping_zip,
    adress_type,
):
    """
    Validate form for whitespces and add shiping address to the order
    """
    if validate_from_for_whitespaces(
        [shipping_address1, shipping_country, shipping_zip]
    ):
        filtered_billing_adress = check_adress_by_street_adress(
            user=user, street_adress=shipping_address1, adress_type=adress_type
        )
        if not filtered_billing_adress:
            shipping_adress = create_a_new_address(
                user=user,
                street_adress=shipping_address1,
                apartment_adress=shipping_address2,
                country=shipping_country,
                zip=shipping_zip,
                adress_type=adress_type,
            )
            add_shipping_adress_to_the_order(
                order=order, adress_queryset=shipping_adress
            )
            check_option_set_default(
                user=user,
                adress_type=adress_type,
                set_default_shipping=set_default_shipping,
                shipping_adress=shipping_adress,
            )
            return shipping_adress
    return "Please fill in all required fields"


def default_shipping_adress(
    user,
    order,
    use_default_shipping,
    set_default_shipping,
    shipping_address1,
    shipping_address2,
    shipping_country,
    shipping_zip,
    adress_type,
):
    """
    Search default shipping adress and default billing adress
    Add shiping adress to the order, if user enable option -
    'save as default' than add this adress to the Adress model
    """
    address_shipping_queryset = filter_and_check_default_adress(
        user=user,
        adress_type="S",
    )
    exist_default_shipping_adress = check_enabled_option_use_default_shipping(
        use_default_shipping=use_default_shipping,
        address_shipping_queryset=address_shipping_queryset,
        order=order,
    )
    if (
        exist_default_shipping_adress
        == "User do not have enabled option save as default"
    ):
        return validate_and_create_a_new_adress(
            user=user,
            order=order,
            set_default_shipping=set_default_shipping,
            shipping_address1=shipping_address1,
            shipping_address2=shipping_address2,
            shipping_country=shipping_country,
            shipping_zip=shipping_zip,
            adress_type=adress_type,
        )
    if exist_default_shipping_adress == "Successfully added to the order":
        # See where we can use this message
        return "User use the default shipping adress"
    return "Please fill in the required shipping address fields"


def check_enabled_option_use_default_shipping(
    use_default_shipping, address_shipping_queryset, order
):
    """Check if user has default shipping adress"""
    if use_default_shipping:
        # Chagne the logic of returns
        return check_default_shipping_adress(
            order=order, address_shipping_queryset=address_shipping_queryset
        )
    return "User do not have enabled option save as default"


def check_default_shipping_adress(order, address_shipping_queryset):
    """
    Check default shipping adress and if exist
    Call another function to add shipping adress to the order
    """
    if address_shipping_queryset:
        # Chagne the logic of returns
        add_shipping_adress_to_the_order(
            order=order, adress_queryset=address_shipping_queryset
        )
        return "Successfully added to the order"
    return "Queryset does not exist"


# Logic for the same billing adress as shipping with enabled and disabled option save


def filtered_billing_adress_and_create_new(
    user,
    order,
    set_default_billing,
    billing_address1,
    shipping_address1,
    shipping_address2,
    shipping_country,
    shipping_zip,
):
    """
    Three layer of logic:
        -Filtering billing adress if not exists then create
        -If user has default billing adress, and enable option 'save as default'
        -Change status the default adress
    """
    filtered_billing_adress = check_adress_by_street_adress(
        user=user, street_adress=billing_address1, adress_type="B"
    )
    if not filtered_billing_adress:
        billing_adress_as_same = create_a_new_address(
            user=user,
            street_adress=shipping_address1,
            apartment_adress=shipping_address2,
            country=shipping_country,
            zip=shipping_zip,
            adress_type="B",
        )
        if set_default_billing:
            address_queryset = filter_and_check_default_adress(
                user=user,
                adress_type="B",
            )
            if address_queryset:
                change_status_default_address(address=address_queryset, status=False)
            change_status_default_address(address=billing_adress_as_same, status=True)
        add_billing_address_to_the_order(
            order=order, adress_queryset=billing_adress_as_same
        )
        return "Created a new billing adress"
    return "Adress exists"


def check_option_default_shipping(
    user,
    order,
    use_default_shipping,
    billing_adress1,
    shipping_address1,
    shipping_address2,
    shipping_country,
    shipping_zip,
    set_default_billing,
    address_shipping_queryset,
):
    """Check enabled option use default shipping"""
    if use_default_shipping:
        add_billing_address_to_the_order(
            order=order, adress_queryset=address_shipping_queryset
        )
        return "Added billing adress to the Order"
    return filtered_billing_adress_and_create_new(
        user=user,
        order=order,
        billing_address1=billing_adress1,
        shipping_address1=shipping_address1,
        shipping_address2=shipping_address2,
        shipping_country=shipping_country,
        shipping_zip=shipping_zip,
        set_default_billing=set_default_billing,
    )


def change_status_default_adress_if_not_exist(
    user,
    address_shipping_queryset,
):
    """Change the status of default adress if exists"""
    filtered_billing_adress = check_adress_by_street_adress(
        user=user,
        street_adress=address_shipping_queryset.street_adress,
        adress_type="B",
    )
    if not filtered_billing_adress:
        billing_adress = create_a_new_address(
            user=user,
            street_adress=address_shipping_queryset.street_adress,
            apartment_adress=address_shipping_queryset.apartment_adress,
            country=address_shipping_queryset.country,
            zip=address_shipping_queryset.zip,
            adress_type="B",
        )
        change_status_default_address(address=billing_adress, status=True)
        return "Default adress has been changed to new"
    else:
        change_status_default_address(address=filtered_billing_adress, status=True)
        return "Default address has been chaned to existent one"


def comprare_shipping_and_billing_adresses(
    user, address_shipping_queryset, address_billing_queryset
):
    """
    Compare shipping and billing adress
    Change the status of default adress if different adresses
    Change the status of default adress if not exists
    """
    if (
        address_shipping_queryset.street_adress
        != address_billing_queryset.street_adress
    ):
        change_status_default_address(address=address_billing_queryset, status=False)
        change_status_default_adress_if_not_exist(
            user=user, address_shipping_queryset=address_shipping_queryset
        )


def check_adress_billing_quresytet(
    user, address_billing_queryset, address_shipping_queryset
):
    """
    Check address billing queryset
    If exists:
        call comparing function
    else:
        Change the status default adress
    """
    if address_billing_queryset:
        comprare_shipping_and_billing_adresses(
            user=user,
            address_billing_queryset=address_billing_queryset,
            address_shipping_queryset=address_shipping_queryset,
        )
    else:
        change_status_default_adress_if_not_exist(
            user=user, address_shipping_queryset=address_shipping_queryset
        )


def check_set_default_shipping_adress(
    user,
    order,
    address_shipping_queryset,
    set_default_billing,
    address_billing_queryset,
):
    """
    Check option of default shipping adress
    If enabled check adress billing queryset
    Else filtering billing adress and create new
    """
    if set_default_billing:
        check_adress_billing_quresytet(
            user=user,
            address_shipping_queryset=address_shipping_queryset,
            address_billing_queryset=address_billing_queryset,
        )
    else:
        filtered_billing_adress_and_create_new(
            user=user,
            order=order,
            billing_address1=address_shipping_queryset.street_adress,
            shipping_address1=address_shipping_queryset.street_adress,
            shipping_address2=address_shipping_queryset.apartment_adress,
            shipping_country=address_shipping_queryset.country,
            shipping_zip=address_shipping_queryset.zip,
            set_default_billing=set_default_billing,
        )


def the_same_billing_logic(
    user,
    order,
    same_billing_address,
    use_default_shipping,
    billing_adress1,
    shipping_address1,
    shipping_address2,
    shipping_country,
    shipping_zip,
    set_default_billing,
):
    """
    The same billing adress
    Quite complicated logic that includes checking all possible options for pressing buttons:
        -Billing address is the same as my shipping address
        -Save as default shipping address
        -Save as default billing address
    """
    address_shipping_queryset = filter_and_check_default_adress(
        user=user,
        adress_type="S",
    )
    address_billing_queryset = filter_and_check_default_adress(
        user=user,
        adress_type="B",
    )
    if same_billing_address:
        if (
            check_option_default_shipping(
                user=user,
                order=order,
                use_default_shipping=use_default_shipping,
                billing_adress1=billing_adress1,
                shipping_address1=shipping_address1,
                shipping_address2=shipping_address2,
                shipping_country=shipping_country,
                shipping_zip=shipping_zip,
                address_shipping_queryset=address_shipping_queryset,
                set_default_billing=set_default_billing,
            )
            == "Added billing adress to the Order"
        ):
            check_set_default_shipping_adress(
                user=user,
                order=order,
                address_shipping_queryset=address_shipping_queryset,
                set_default_billing=set_default_billing,
                address_billing_queryset=address_billing_queryset,
            )


# Logic if both options are disabled:
#   Billing address is the same as my shipping address
#   Save as default billing address


def disabled_billing_and_default_logic(
    user,
    order,
    same_billing_address,
    use_default_billing,
    set_default_billing,
    billing_address1,
    billing_address2,
    billing_country,
    billing_zip,
    adress_type,
):
    """
    The logic if user disable 2 options:
        -Billing address is the same as my shipping address
        -Save as default shipping address
    """
    if not any((same_billing_address, use_default_billing)):
        return validate_and_create_a_new_adress(
            user=user,
            order=order,
            set_default_shipping=set_default_billing,
            shipping_address1=billing_address1,
            shipping_address2=billing_address2,
            shipping_country=billing_country,
            shipping_zip=billing_zip,
            adress_type=adress_type,
        )
    return "Please fill in the required shipping address fields"


# Logic to create devilered object and delete order


def create_delivered_object_item(user):
    """Create devilered object item"""
    orders = get_all_objects_from_order_items()
    quantity, _ = get_information_about_order(orders=orders)
    summary_items_string = convert_order_items_into_string_view(orders=orders)
    create_a_new_devilered_order_object(
        user=user, summary_items=summary_items_string, quantity=quantity
    )


def delete_order_and_order_items(user):
    """Delete order and order items"""
    orders = get_all_objects_from_order_items()
    delete_all_items_from_order(orders=orders)
    delete_order(user=user, ordered=False)
    return True
