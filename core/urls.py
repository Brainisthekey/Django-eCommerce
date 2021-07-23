from django.urls import path
from core.views import checkout, HomeView, ItemDetailView, add_to_cart, remove_from_cart, OrderSummaryView, remove_single_item_from_cart

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('checkout/', checkout, name='checkout'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
]