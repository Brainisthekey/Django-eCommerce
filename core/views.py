from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.detail import DetailView
from core.models import Item, OrderItem, Order
from django.views.generic import ListView
from django.utils import timezone
from django.contrib import messages

def checkout(request):
    return render(request, 'checkout-page.html')

class HomeView(ListView):
    
    model = Item
    paginate_by = 2
    template_name = 'home-page.html'
    context_object_name = 'items'

class ItemDetailView(DetailView):

    model = Item
    template_name = 'product-page.html'


def add_to_cart(request, slug):
    
    #item = Item.object.filter(slug=slug).first
    #if item: ....

    item = get_object_or_404(Item, slug=slug)
    #order_item = OrderItem.objects.create(item=item) #Проблема вот здесь, так как мы создаём новый обьект в любой случае
    order_item, _ = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_queryset = Order.objects.filter(user=request.user, ordered=False)
    if order_queryset.exists():
        order = order_queryset[0]
        # Check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated")
            return redirect('core:product', slug=slug)
        else:
            order.items.add(order_item)
            messages.info(request, "This item was aded tou your cart")
            return redirect('core:product', slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was aded tou your cart")
        return redirect('core:product', slug=slug)

def remove_from_cart(request, slug):

    item = get_object_or_404(Item, slug=slug)
    order_queryset = Order.objects.filter(user=request.user, ordered=False)
    if order_queryset.exists():
        order = order_queryset[0]
        # Check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.get_or_create(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart")
            return redirect('core:product', slug=slug)
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('core:product', slug=slug)
    else:
        # add a message saying the user doesn't have an order
        messages.info(request, "You do not have an active order yet")
        return redirect('core:product', slug=slug)
