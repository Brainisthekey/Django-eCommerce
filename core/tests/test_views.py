from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from core.models import Item, Order, Adress, Coupon, OrderItem
from django.utils import timezone
from django.contrib.auth import get_user_model


#I would change the name to - TestViewsForAuthorizatedUser
class TestViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.coupon = Coupon.objects.create(code='test', amount=5)
        cls.user = User.objects.create(username='test')
        cls.user.set_password('testpassword')
        cls.user.save()
        cls.c = Client()
        cls.c.login(username='test', password='testpassword')
        cls.item = Item.objects.create(
            title='test_product',
            price=20,
            discount_price=15,
            description='test_description',
            category='R',
            lable='P',
            slug='verity',
            image='test'
        )
        cls.adress = Adress.objects.create(
            user=cls.user,
            street_adress='test',
            apartment_adress='test',
            country='Ukraine',
            zip='test',
            adress_type='B',
            default=True
        )
        cls.order = Order.objects.create(
            user=cls.user,
            start_date=timezone.now(),
            ordered_date=timezone.now(),
            ordered=False,
            billing_adress=cls.adress,
            shipping_adress=cls.adress,
            coupon=cls.coupon,
        )
        cls.order_item = OrderItem.objects.create(
            quantity=1,
            ordered=False,
            item=cls.item,
            user=cls.user
        )
        cls.order.items.add(cls.order_item)

    def test_url_allowed_hosts_home_page(self):
        """Test connection to home page"""
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home-page.html')
    
    def test_home_page_html(self):
        """Test home page context"""
        response = self.c.get('/')
        html = response.content.decode('utf-8')
        self.assertIn('test_product', html)
        self.assertIn('5.0', html)
        self.assertIn('R', html)
        self.assertIn('P', html)
        self.assertIn('verity', html)
        self.assertIn('test', html)


    def test_url_allowed_hosts_product_page(self):
        """Test the Product page"""
        response = self.c.get(reverse('core:product', args=['verity']))
        html = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product-page.html')
        self.assertIn('test_product', html)

    def test_order_summary_view(self):
        response = self.c.get(reverse('core:order-summary'), follow=True)
        html = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order-summary.html')

        #Assert for regular price
        self.assertIn('$20.0', html)

        #Assert for discount price
        self.assertIn('$15.0', html)

        #Assert for total price
        self.assertIn('$10.0', html)

        #Assert for coupon
        self.assertIn('$5.0', html)

        #Assert for quantity
        self.assertIn('1', html)

    def test_checkout_view(self):
        response = self.c.get(reverse('core:checkout'), follow=True)
        html = response.content.decode('utf-8')
        #self.assertIn('Your cart is empty', html)
        #self.assertTemplateUsed('checkout.html')



