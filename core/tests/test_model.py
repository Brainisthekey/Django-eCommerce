from django.test import TestCase
from django.utils import timezone
from core.models import Adress, Coupon, Item, Order, OrderItem
from django.contrib.auth.models import User


class TestAppModels(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username='test', password='user')
        self.coupon = Coupon.objects.create(code='test', amount=5)
        self.adress = Adress.objects.create(
            user=self.user,
            street_adress='test',
            apartment_adress='test',
            country='Ukraine',
            zip='test',
            adress_type='B',
            default=True
        )
        self.item = Item.objects.create(
            title='test',
            price=10,
            discount_price=5,
            description='test',
            category='R',
            lable='P',
            slug='test',
            image='test'
        )
        self.item_2 = Item.objects.create(
            title='test_2',
            price=10,
            discount_price=8,
            description='test_2',
            category='B',
            lable='P',
            slug='test_2',
            image='test_2'
        )
        self.order_item = OrderItem.objects.create(
            quantity=1,
            ordered=False,
            item=self.item,
            user=self.user
        )
        self.order_item_2 = OrderItem.objects.create(
            quantity=2,
            ordered=False,
            item=self.item_2,
            user=self.user
        )
        self.order = Order.objects.create(
            user=self.user,
            start_date=timezone.now(),
            ordered_date=timezone.now(),
            ordered=False,
            billing_adress=self.adress,
            shipping_adress=self.adress,
            coupon=self.coupon,
        )


    def test_coupon_model_representation(self):
        """Test Coupon model representation"""
        self.assertEqual(str(self.coupon), 'test')

    def test_adress_model_representation(self):
        """Test Adress model representation"""
        self.assertEqual(str(self.adress), 'test')

    def test_model_item(self):
        """Test model Item"""
        self.assertEqual(self.item.get_absolute_url(), '/product/test/')
        self.assertEqual(self.item.get_add_to_cart_url(), '/add-to-cart/test/')
        self.assertEqual(self.item.get_remove_from_cart_url(), '/remove-from-cart/test/')
        self.assertEqual(str(self.item), 'test')

    def test_model_order_item(self):
        """Test model Order Item"""

        order_item = OrderItem.objects.create(
            quantity=1,
            ordered=False,
            item=self.item,
            user=self.user
        )
        self.assertEqual(order_item.get_total_item_price(), 10)
        self.assertEqual(order_item.get_total_item_discount_price(), 5)
        self.assertEqual(order_item.get_amount_saved(), 5)
        self.assertEqual(order_item.get_finall_price(), 5)
        self.item.discount_price=None
        self.assertEqual(order_item.get_finall_price(), 10)
        self.assertEqual(str(order_item), '1 of test')
    
    def test_order(self):
        """Test model Order"""
        #Many to many fileds
        self.order.items.set([self.order_item.pk, self.order_item_2.pk])
        self.assertEqual(self.order.items.count(), 2)
        self.assertEqual(self.order.items.first().quantity, 1)
        self.assertEqual(self.order.items.last().quantity, 2)
        self.assertEqual(str(self.order), 'test')
        self.assertEqual(self.order.get_total(), 16)



