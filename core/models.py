from django.conf import settings
from django.urls import reverse
from django.db import models
from django_countries.fields import CountryField
from django.db.models.fields import CharField, IntegerField, TextField


CATEGORY_CHOICES = (
    ("R", "Romance"),
    ("B", "Business & Investing"),
    ("E", "Education & Reference"),
)

LABEL_CHOICES = (
    ("P", "primary"),
    ("S", "secondary"),
    ("D", "danger")
)

ADRESS_CHOICES = (
    ("B", "Billing"),
    ("S", "Shipping"),
)


class Item(models.Model):
    """Item(Book) model"""

    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    description = models.TextField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=1)
    lable = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    image = models.ImageField()

    def get_absolute_url(self):
        """Get absolute url to the items"""
        return reverse("core:product", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        """Get absulte url to add too cart view"""
        return reverse("core:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        """Get abslute url for remove from cart"""
        return reverse("core:remove-from-cart", kwargs={"slug": self.slug})

    def __str__(self):
        """Returning represenntation of Item(Book) title"""
        return self.title


class OrderItem(models.Model):
    """Order items model"""

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def get_total_item_price(self):
        """Get total item price"""
        return self.quantity * self.item.price

    def get_total_item_discount_price(self):
        """Get total itemm discount price"""
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        """The difference between the starting price and the discount"""
        return self.get_total_item_price() - self.get_total_item_discount_price()

    def get_finall_price(self):
        """Get total price of item"""
        if self.item.discount_price:
            return self.get_total_item_discount_price()
        return self.get_total_item_price()

    def __str__(self):
        """Returning representation of Item title and quantity"""
        return f"{self.quantity} of {self.item.title}"


class Order(models.Model):
    """The users order"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_adress = models.ForeignKey(
        "Adress",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="billing_adress",
    )
    shipping_adress = models.ForeignKey(
        "Adress",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shipping_adress",
    )
    coupon = models.ForeignKey("Coupon", on_delete=models.SET_NULL, null=True, blank=True)

    def get_total(self):
        """Get total sum of the order"""
        total = 0
        for order_item in self.items.all():
            total += order_item.get_finall_price()
        if self.coupon and self.items.all():
            total -= self.coupon.amount
        return total

    def __str__(self):
        """Returning representation of username"""
        return self.user.username


class OrderDevilevered(models.Model):
    """Devilered order items"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    summary_items = TextField(max_length=1000)
    quantity = IntegerField(default=1)


class Adress(models.Model):
    """Adress model"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_adress = models.CharField(max_length=100)
    apartment_adress = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    adress_type = models.CharField(max_length=1, choices=ADRESS_CHOICES)
    default = models.BooleanField(default=False)

    class Meta:
        """Plural adress dispay"""

        verbose_name_plural = "Adressess"

    def __str__(self):
        """Returning representation of user"""
        return self.user.username


class Coupon(models.Model):
    """Coupon model"""

    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        """Returning the coupon code"""
        return self.code
