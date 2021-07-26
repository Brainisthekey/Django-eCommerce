from django.urls import path
from core.views import CheckoutView, HomeView, ItemDetailView, add_to_cart, remove_from_cart, OrderSummaryView, remove_single_item_from_cart, AddCouponView, RomanceView, EducationReferenceView, BusinessInvestingView, SearchResult

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('romance/', RomanceView.as_view(), name='romance'),
    path('business-investing/', BusinessInvestingView.as_view(), name='business-investing'),
    path('education-reference/', EducationReferenceView.as_view(), name='education-reference'),
    path('search/', SearchResult.as_view(), name='search')
]