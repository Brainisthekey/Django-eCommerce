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


    