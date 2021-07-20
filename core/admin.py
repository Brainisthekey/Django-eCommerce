from django.contrib import admin
from core.models import Item, OrderItem, Order


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
