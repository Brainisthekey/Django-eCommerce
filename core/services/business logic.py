from core.services.db_services import get_all_objects_from_order_items


def delete_order_if_order_items_empty():
    if get_all_objects_from_order_items.count() == 0:
        pass



    