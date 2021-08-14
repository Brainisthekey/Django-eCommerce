from django.db.models.query_utils import Q
from django.utils import timezone
from core.models import Adress, Order, Item, OrderDevilevered, OrderItem, Coupon
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages


# Operation with model Item

def filtering_items_by_caegories(category):
    """Filtering model Item by category"""
    return Item.objects.filter(category=category).all()


def filtering_items_by_icontains_filter(query):
    """Filtering model Item by Q(icontains)"""
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
    #Actually here we must to return ObjectDoesNotExist, not None
    return None


def create_order_object(user):
    """Create a new order"""
    ordered_date = timezone.now()
    return Order.objects.create(user=user, ordered_date=ordered_date)


def add_shipping_adress_to_the_order(order, adress_queryset):
    """Add shipping address to the order"""
    order.shipping_adress = adress_queryset
    save_order_changes(order)
    

def add_billing_address_to_the_order(order, adress_queryset):
    """Add billing address to the order"""
    order.billing_adress = adress_queryset
    save_order_changes(order)


def add_item_to_the_order(order, order_item):
    """Add order item to the order"""
    order.items.add(order_item)


def remove_item_from_orders(user, slug, ordered):
    """Remove definite item from Order model"""
    filter_order_objects(user=user, ordered=False).items.remove(filter_order_item_objects(user=user, slug=slug, ordered=False))


def delete_order(user, ordered):
    """Delete Order if order items is empty"""
    filter_order_objects(user=user, ordered=False).delete()


# Operation with model OrderItems

def get_all_objects_from_order_items():
    """Get all objects from OrderItem model"""
    return OrderItem.objects.all()


def delete_all_items_from_order(orders):
    """Delete all items from OrderItem model"""
    orders.delete()


def get_order_item_or_create(user, slug):
    """Get or create order item object"""
    item = get_object_or_404(klass=Item, slug=slug)
    return OrderItem.objects.get_or_create(
        user=user,
        item=item,
        ordered=False
    )[0]


def change_order_quantity(order_item):
    """Change quantity order"""
    order_item.quantity += 1
    order_item.save()


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
    item = get_object_or_404(klass=Item, slug=slug)
    if order_quaryset.items.filter(item__slug=item.slug).exists():
        return order_quaryset.items.filter(item__slug=item.slug)
    return None


def delete_item_from_order_items(user, slug, ordered):
    """Delete item from OrderItem model"""
    filter_order_item_objects(user=user, slug=slug, ordered=False).delete()


def check_item_order_quantity(item):
    """Change order item quantity if OrderItem quantity more than 1"""
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()


def get_order_quantity(order):
    """Get order quantity"""
    return order.quantity


def get_order_item_title(order):
    """Get order itemm title"""
    return order.item.title


# Operation with model Coupon
   
def get_coupon(request, code):
    """Get coupon object if exists"""
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

# Operation with model Address

def filter_and_check_default_adress(user, adress_type, default):
    """Check and filter Address model for default billing and shipping address"""
    adress = Adress.objects.filter(
        user=user,
        adress_type=adress_type,
        default=True
    )
    if adress.exists():
        return adress.first()
    return None


def check_adress_by_street_adress(user, street_adress, adress_type):
    """Chek adress in Adress model by street adress"""
    adress = Adress.objects.filter(
        user=user,
        street_adress=street_adress,
        adress_type=adress_type,
    )
    if adress.exists():
        return adress.first()
    return None


def create_a_new_address(user, street_adress, apartment_adress, country, zip, adress_type):
    """Create a new addresss"""
    adress = Adress(
        user=user,
        street_adress=street_adress,
        apartment_adress=apartment_adress,
        country=country,
        zip=zip,
        adress_type=adress_type
    )
    adress.save()
    return adress


def change_status_default_address(address, status):
    """Change status of default adress if exists"""
    address.default = status
    address.save()


def change_pk_of_address(address):
    """Change pk of address"""
    address.pk = None
    address.save()


def change_address_type_for_billing(address):
    """Change address type for billing"""
    address.adress_type = 'B'
    address.save()

# Operation with OrderDelivered model

def create_a_new_devilered_order_object(user, summary_items, quantity):
    """Create a new devilered order objects"""
    OrderDevilevered.objects.create(
        user=user,
        summary_items=summary_items,
        quantity=quantity
    )
