from core.models import Order
from django.shortcuts import get_object_or_404
from core.models import Item, OrderItem

# Operation with model Order
# Operation with model OrderItems
# Operation with model Adress
# Operation with model ??
def get_order_objects(user, ordered):
    """Get objects from Order model"""
    return Order.objects.get(user=user, ordered=False)

def get_all_objects_from_order_items():
    """Get all objects from OrderItem model"""
    return OrderItem.objects.all()

def filter_order_objects(user, ordered):
    # TODO: Think about returning a first element becouse
    # I have only 1 order
    """Filtering objects in Order model"""
    if Order.objects.filter(user=user, ordered=False).exists():
        return Order.objects.filter(user=user, ordered=False).first()
    return None

def filter_order_item_objects(user, slug, ordered):
    """Filtering objects in OrderItem model"""
    item = get_object_or_404(klass=Item, slug=slug)
    return OrderItem.objects.filter(
        user=user,
        item=item,
        ordered=False
    ).first()

def filter_order_item_objects_by_slag(user, slug, order_quaryset, ordered):
    """Filtering objects in OrderItem model by slag"""
    #Maybe will have an error
    item = get_object_or_404(klass=Item, slug=slug)
    if order_quaryset.items.filter(item__slug=item.slug).exists():
        return order_quaryset.items.filter(item__slug=item.slug)
    return None

def remove_item_from_orders(user, slug, ordered):
    filter_order_objects(user=user, ordered=False).items.remove(filter_order_item_objects(user=user, slug=slug, ordered=False))

def delete_item_from_order_items(user, slug, ordered):
    filter_order_item_objects(user=user, slug=slug, ordered=False).delete()

def delete_order_if_order_items_empty(user, ordered):
    filter_order_objects(user=user, ordered=False).delete()

def filter_adress_objects(user, adress_type, default):
    """Filtering objects in Adress model"""
    # TODO

