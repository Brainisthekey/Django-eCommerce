from django.urls import path
from core.views import item_list, home, checkout

app_name = 'core'

urlpatterns = [
    path('', home, name='home'),
    path('product/', item_list, name='item-list'),
    path('checkout/', checkout, name='checkout'),
]