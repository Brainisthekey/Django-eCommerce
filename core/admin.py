from django.contrib import admin
from core.models import Item, OrderItem, Order, Coupon, Adress, OrderDevilevered


class OrderAdmin(admin.ModelAdmin):

    list_display = ['user', 'ordered', 'billing_adress', 'shipping_adress', 'coupon']
    list_display_links = ['user', 'billing_adress', 'shipping_adress', 'coupon']
    list_filter = ['ordered']
    search_fields = ['user__username']

class AdressAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'street_adress',
        'apartment_adress',
        'country',
        'zip',
        'adress_type',
        'default',
    ]
    list_filter = ['default', 'adress_type', 'country']
    search_fields = ['user', 'street_adress', 'apartment_adress', 'zip']


admin.site.register(Item)
admin.site.register(Coupon)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Adress, AdressAdmin)
admin.site.register(OrderDevilevered)
