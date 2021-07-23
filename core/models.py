from django.db import models
from django.conf import settings
from django.urls import reverse


CATEGORY_CHOICES = (
    ('R', 'Romance'),
    ('C', 'Classics'),
    ('H', 'Horror')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)


class Item(models.Model):

    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    description = models.TextField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=1)
    lable = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()

    def get_absolute_url(self):
        return reverse('core:product', kwargs={
            'slug': self.slug
        })
    
    def get_add_to_cart_url(self):
        return reverse('core:add-to-cart', kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse('core:remove-from-cart', kwargs={
            'slug': self.slug
        })

    def __str__(self):
        return self.title

class OrderItem(models.Model):
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_item_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_item_discount_price()

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

class Order(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
        