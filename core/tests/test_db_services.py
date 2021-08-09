from core.services.db_services import filtering_items_by_caegories
from django.test import TestCase
from core.models import Item, OrderItem, Order, Adress, Coupon
from django.contrib.auth.models import User
from django.utils import timezone


class TestDBCommands(TestCase):

    def test_filtering_items_by_categories(self):
        """
        Question there
        Can realise with helo of def SetUp,
        Orders, Items, Order Items will create before each tests
        """
        pass

    def setUp(self):
        self.user = User.objects.create_user('testusername', 'test@test.com', 'testpassword')
        self.coupon = Coupon.objects.create(code='test', amount=5)
        self.item = Item.objects.create(
            title='test',
            price=30,
            discount_price=25,
            description='test',
            category='R',
            lable='P',
            slug='test',
            image='verity'
        )
        self.order_item = OrderItem.objects.create(
            quantity=1,
            ordered=False,
            item=self.item,
            user=self.user
        )
        self.adress = Adress.objects.create(
            user=self.user,
            street_adress='test',
            apartment_adress='test',
            country='Ukraine',
            zip='test',
            adress_type='B',
            default=True
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
        self.order.items.add(self.order_item)
        
    def test_deleting_order(self):

        print(Order.objects.all())
        self.order.delete()
        self.assertEqual(Order.objects.all().count(), 0)

    def test_check_setup_mode(self):
        
        #Yeach, it's working for me,
        #When we run a new tests we SetUp a new enviorenment!
        self.assertEqual(Order.objects.all().count(), 1)
    
        

    
