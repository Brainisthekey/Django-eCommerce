from django.db.models.query_utils import Q
from core.models import Order
from django.shortcuts import get_object_or_404
from core.models import Item, OrderItem, Coupon
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages


# Operation with model Item

def filtering_items_by_caegories(category):
    return Item.objects.filter(category=category).all()

def filtering_items_by_icontains_filter(query):
    return Item.objects.filter(Q(title__icontains=query))

# Operation with model Order

def get_order_objects(user, ordered):
    """Get objects from Order model"""
    return Order.objects.get(user=user, ordered=False)

def save_order_changes(order):
    """Save the order changes"""
    order.save()

def filter_order_objects(user, ordered):
    """Filtering objects in Order model"""
    if Order.objects.filter(user=user, ordered=False).exists():
        return Order.objects.filter(user=user, ordered=False).first()
    return None

def remove_item_from_orders(user, slug, ordered):
    """Remove definite item from Order model"""
    filter_order_objects(user=user, ordered=False).items.remove(filter_order_item_objects(user=user, slug=slug, ordered=False))

def delete_order_if_order_items_empty(user, ordered):
    """Delete Order if order items is empty"""
    filter_order_objects(user=user, ordered=False).delete()

def delete_order_if_order_items_empty(user, ordered):
    """Delete order in Order model if OrderItems is empty"""
    filter_order_objects(user=user, ordered=False).delete()

# Operation with model OrderItems

def get_all_objects_from_order_items():
    """Get all objects from OrderItem model"""
    return OrderItem.objects.all()

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

def delete_item_from_order_items(user, slug, ordered):
    """Delete item from OrderItem model"""
    filter_order_item_objects(user=user, slug=slug, ordered=False).delete()

def check_item_order_quantity(item):
    """Change order quantity if OrderItem quantity more than 1"""
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

# Operation with model Coupon
   
def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return None

def check_user_for_active_coupon(order):
    """Check Order for active coupon"""
    if order.coupon:
        return order.coupon
    return None


def add_and_save_coupon_to_the_order(order, request, code):
    """Add coupon to the order"""
    order.coupon = get_coupon(request=request, code=code)
    save_order_changes(order)

def check_user_for_active_coupon(order):
    """Check User for active coupon at this order"""
    if order.coupon:
        return order.coupon
    return None

# Other
