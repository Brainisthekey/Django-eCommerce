from core.services.db_services import filtering_items_by_caegories, filtering_items_by_icontains_filter, get_order_objects, save_order_changes, filter_order_objects, create_order_object, add_shipping_adress_to_the_order, add_billing_address_to_the_order, add_item_to_the_order, remove_item_from_orders, delete_order, get_all_objects_from_order_items, delete_all_items_from_order, get_order_item_or_create, change_order_quantity, filter_order_item_objects, filter_order_item_objects_by_slag, delete_item_from_order_items, check_item_order_quantity, get_order_quantity, get_order_item_title, get_coupon, check_user_for_active_coupon
from django.test import TestCase
from core.models import Item, OrderItem, Order, Adress, Coupon
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import Http404


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


        #Check if order doesn't exist, raise an Error - ObjectDoesNotExist
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

    def test_remove_item_from_orders(self):
        """Test query to remove Item from Order"""

        #Add Item to the Order
        add_item_to_the_order(order=self.order, order_item=self.order_item)
        
        #Remove Item from Order
        remove_item_from_orders(user=self.user, slug='test', ordered=False)
        
        #Assert that Item has been removed from the Order
        self.assertEqual(self.order.items.all().count(), 0)

    def test_delete_order(self):
        """Test query to delete Order"""

        #Delete Order
        delete_order(user=self.user, ordered=False)

        #Check that Order doesn't exist
        self.assertEqual(Order.objects.all().count(), 0)


#Testing query to model OrderItem

    def test_get_all_objects_from_order_items(self):
        """Test query to GET all object from the order"""

        #Assert amount of OrderItems
        self.assertEqual(get_all_objects_from_order_items().count(), 1)

    def test_delete_all_items_from_order(self):
        """Test query to delete all items from the Order Item"""
        
        #Assert OrderItems objects all
        self.assertEqual(OrderItem.objects.all().count(), 1)

        #Delete all items from the OrderItems
        delete_all_items_from_order(orders=self.order_item)

        #Assert OrderItems have been removed
        self.assertEqual(OrderItem.objects.all().count(), 0)

    def test_get_order_item_or_create(self):
        """Test query to get or create OrderItem object"""

        #Test with existens Item
        self.assertEqual(get_order_item_or_create(user=self.user, slug='test').item.title, 'test')

        #Test with non existens Item, raise an Error - HTTP404
        with self.assertRaises(Http404):
           get_order_item_or_create(user=self.user, slug='fail-test')

    def test_change_order_quantity(self):
        """Test query to change OrderItem quantity"""

        #Assert current quantity of ordered items
        self.assertEqual(self.order_item.quantity, 1)

        #Change the OrderItem quantity
        change_order_quantity(self.order_item)

        #Assert that quantity has been changed
        self.assertEqual(self.order_item.quantity, 2)

    def test_filter_order_item_objects(self):
        """Test query to filtering OrderItems object"""

        #Test with existens Item
        self.assertEqual(filter_order_item_objects(user=self.user, slug='test', ordered=False).item.title, 'test')

        #Test with non existens Item, raise an Error - HTTP404
        with self.assertRaises(Http404):
           filter_order_item_objects(user=self.user, slug='fail-test', ordered=False)


    def test_filter_order_item_objects_by_slag(self):
        """Test query to filtering OrderItems object by <slag>"""

        self.order.items.add(self.order_item)
        #Test with existens Item
        self.assertEqual(filter_order_item_objects_by_slag(user=self.user, slug='test', order_quaryset=self.order, ordered=False).first().item.title, 'test')

        #Test with non existens Item, raise an Error - HTTP404
        with self.assertRaises(Http404):
           filter_order_item_objects(user=self.user, slug='fail-test', ordered=False)
        
    def test_delete_item_from_order_items(self):
        """Test query to deleting selected Item from OrderItem"""

        #Assert current OrderItem amount equal 1
        self.assertEqual(OrderItem.objects.all().count(), 1)

        #Delete OrderItem
        delete_item_from_order_items(user=self.user, slug='test', ordered=False)

        #Assert current OrderItem amount equl 0
        self.assertEqual(OrderItem.objects.all().count(), 0)

    def test_check_item_order_quantity(self):
        """Test query to changing OrderItem quantity"""
        
        #Change OrderItem quantity to 2
        self.order_item.quantity = 2

        #Situation when OrderItem quantity more than 1
        check_item_order_quantity(item=self.order_item)

        #Assert OrderItem must have to changed to 1
        self.assertEqual(self.order_item.quantity, 1)

    def test_get_order_quantity(self):
        """Test query to get OrderItem quantity"""
        
        #Assert OrderItem quantity 
        self.assertEqual(get_order_quantity(order=self.order_item), 1)


    def test_get_order_item_title(self):
        """Test query to get the OrderItem title"""

        #Assert OrderItem title
        self.assertEqual(get_order_item_title(order=self.order_item), 'test')

#Testing query to model Coupon

    def test_get_coupon(self):
        """Test query to get coupon object if exists else Object doesn't exist"""

        #Assert the coupon which doesn't exist
        #And becaouse we don't have a try except block, we can't check that ErrorRaises
        self.assertIsNone(get_coupon(code='Does not exist'))
        
        #Get the coupon which exist
        self.assertEqual(get_coupon(code='test'), self.coupon)

    def test_check_user_for_active_coupon(self):
        """Test query to check the Order for active coupon"""

        #Situation when Order has a coupon
        self.assertEqual(check_user_for_active_coupon(order=self.order), self.coupon)

        #Set coupon to None
        self.order.coupon = None

        #Situation when Order doesn't have an active coupon
        self.assertIsNone(check_user_for_active_coupon(order=self.order))

    def 
        