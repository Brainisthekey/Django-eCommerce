from django.contrib import admin
from core.models import Item, OrderItem, Order, Coupon


class OrderAdmin(admin.ModelAdmin):

    list_display = ['user', 'ordered']

admin.site.register(Item)
admin.site.register(Coupon)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
