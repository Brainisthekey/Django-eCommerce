from core.services.db_services import filtering_items_by_caegories, filtering_items_by_icontains_filter, get_order_objects, save_order_changes, filter_order_objects, create_order_object, add_shipping_adress_to_the_order, add_billing_address_to_the_order, add_item_to_the_order
from django.test import TestCase
from core.models import Item, OrderItem, Order, Adress, Coupon
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


class TestDBCommands(TestCase):

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
        self.another_item = Item.objects.create(
            title='test2',
            price=50,
            discount_price=35,
            description='test2',
            category='B',
            lable='P',
            slug='test2',
            image='While_We_Were_Dating',
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

#Testing query to model Item

    def test_filtering_items_by_caegories(self):
        """Test query filtering to model Item"""
        
        #Check amount of items in this category - R
        self.assertEqual(filtering_items_by_caegories(category='R').count(), 1)

        #Check amount of items in not existes category
        self.assertEqual(filtering_items_by_caegories(category='E').count(), 0)

        #Check if title filtered items are the same which was created
        self.assertEqual(filtering_items_by_caegories(category='R').first().title, 'test')

    def test_filtering_items_by_icontains_filter(self):
        """Test query filtering model Item by Q(icontains)"""
        
        #Search amount of items using Q filter
        self.assertEqual(filtering_items_by_icontains_filter(query='test').count(), 2)

        #Check amount of items in not existes category
        self.assertEqual(filtering_items_by_icontains_filter(query='non-exists').count(), 0)

        #Check if title filtered items are the same which was created
        self.assertEqual(filtering_items_by_icontains_filter(query='test').first().title, 'test')

#Testing query to model Order

    def test_get_order_objects(self):
        """Test query to get object from Order model"""

        #Check existent order
        self.assertEqual(get_order_objects(user=self.user, ordered=False), self.order)


        #Check if order doesn't exist
        self.order.delete()
        with self.assertRaises(ObjectDoesNotExist):
            get_order_objects(user=self.user, ordered=False)

#Question here

    def test_save_order_changes(self):
        """
        Test query to save changes on order

        Okay this is actually a stupid thing what I do,
        Because we don't need save the changes ?!
        """
        pass

    def test_filter_order_objects(self):
        """Test query filtering object in Order model"""
        
        #Check existent order
        self.assertEqual(filter_order_objects(user=self.user, ordered=False).ordered, False)

        #Check if order doesn't exist
        self.order.delete()
        self.assertEqual(filter_order_objects(user=self.user, ordered=False), None)

    def test_create_order_object(self):
        """Test query to create a new Order"""

        #Create a new order
        create_order_object(self.user)

        #Check if order has been created
        self.assertEqual(Order.objects.all().count(), 2)

    def test_add_shipping_adress_to_the_order(self):
        """Test query to add shipping adress to the Order"""
        
        #Add sjipping adress to the order
        add_shipping_adress_to_the_order(order=self.order, adress_queryset=self.adress)

        #Assert shipping adress in Order
        self.assertEqual(self.order.shipping_adress, self.adress)

    def test_add_billing_address_to_the_order(self):
        """Test query to add billing adress to the Order"""

        #Add billing adress to the order
        add_billing_address_to_the_order(order=self.order, adress_queryset=self.adress)

        #Assert billing adress in Order
        self.assertEqual(self.order.billing_adress, self.adress)

    def test_add_item_to_the_order(self):
        """Test query to add Item to the Order"""

        #Add Item to the Order
        add_item_to_the_order(order=self.order, order_item=self.order_item)

        #Assert that Item has been added to the Order
        self.assertEqual(self.order.items.all().count(), 1)

    

