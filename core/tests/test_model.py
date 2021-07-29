from django.test import TestCase
from django.utils import timezone
from core.models import Adress, Coupon, Item, Order, OrderItem
from django.contrib.auth.models import User

class TestAppModels(TestCase):
    

    def test_coupon_model_representation(self):
        """Test Coupon model representation"""
        coupon = Coupon.objects.create(code='test', amount=5)
        self.assertEqual(str(coupon), 'test')

    def test_adress_model_representation(self):
        """Test Adress model representation"""
        user = User.objects.create(username='test', password='user')
        adress = Adress.objects.create(
            user=user,
            street_adress='test',
            apartment_adress='test',
            country='Ukraine',
            zip='test',
            adress_type='B',
            default=True
        )
        self.assertEqual(str(adress), 'test')

    def test_model_item(self):
        """Test model Item"""
        item = Item.objects.create(
            title='test',
            price=10,
            discount_price=5,
            description='test',
            category='R',
            lable='P',
            slug='test',
            image='test'
        )
        #TODO test function get_absolute_path
        self.assertEqual(item.get_absolute_url(), '/product/test/')
        self.assertEqual(item.get_add_to_cart_url(), '/add-to-cart/test/')
        self.assertEqual(item.get_remove_from_cart_url(), '/remove-from-cart/test/')
        self.assertEqual(str(item), 'test')

    def test_model_order_item(self):
        """Test model Order Item"""
        user = User.objects.create(username='test', password='user')
        item = Item.objects.create(
            title='test',
            price=5,
            discount_price=4,
            description='test',
            category='R',
            lable='P',
            slug='test',
            image='test'
        )
        order_item = OrderItem.objects.create(
            quantity=1,
            ordered=False,
            item=item,
            user=user
        )
        self.assertEqual(order_item.get_total_item_price(), 5)
        self.assertEqual(order_item.get_total_item_discount_price(), 4)
        self.assertEqual(order_item.get_amount_saved(), 1)
        self.assertEqual(order_item.get_finall_price(), 4)
        item.discount_price=None
        self.assertEqual(order_item.get_finall_price(), 5)
        self.assertEqual(str(order_item), '1 of test')
    
    def test_order(self):
        """Test model Order"""
        user = User.objects.create(username='test', password='user')
        coupon = Coupon.objects.create(code='test', amount=5)
        item_1 = Item.objects.create(
            title='test',
            price=10,
            discount_price=5,
            description='test',
            category='R',
            lable='P',
            slug='test',
            image='test'
        )
        item_2 = Item.objects.create(
            title='test_2',
            price=10.0,
            discount_price=8,
            description='test_2',
            category='B',
            lable='P',
            slug='test_2',
            image='test_2'
        )
        adress = Adress.objects.create(
            user=user,
            street_adress='test',
            apartment_adress='test',
            country='Ukraine',
            zip='test',
            adress_type='B',
            default=True
        )
        order = Order.objects.create(
            user=user,
            start_date=timezone.now(),
            ordered_date=timezone.now(),
            ordered=False,
            billing_adress=adress,
            shipping_adress=adress,
            coupon=coupon,
        )
        order_item = OrderItem.objects.create(
            quantity=1,
            ordered=False,
            item=item_1,
            user=user
        )
        order_item_2 = OrderItem.objects.create(
            quantity=2,
            ordered=False,
            item=item_2,
            user=user
        )
        #Many to many fileds
        order.items.set([order_item.pk, order_item_2.pk])
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.items.first().quantity, 1)
        self.assertEqual(order.items.last().quantity, 2)
        self.assertEqual(str(order), 'test')
        self.assertEqual(order.get_total(), 16)



