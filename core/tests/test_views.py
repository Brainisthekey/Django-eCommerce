from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from core.models import Item, Order, Adress, Coupon
from django.utils import timezone
from django.contrib.auth import get_user_model

class TestViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.coupon = Coupon.objects.create(code='test', amount=5)
        cls.user = User.objects.create(username='test', password='user')
        cls.c = Client()
        cls.item = Item.objects.create(
            title='test_product',
            price=10,
            discount_price=5,
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

    def test_url_allowed_hosts_home_page(self):
        """Test connection to home page"""
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('home-page.html')
    
    def test_home_page_html(self):
        response = self.c.get('/')
        html = response.content.decode('utf-8')
        self.assertIn('test_product', html)
        self.assertIn('5.0', html)
        self.assertIn('R', html)
        self.assertIn('P', html)
        self.assertIn('verity', html)
        self.assertIn('test', html)


    def test_url_allowed_hosts_product_page(self):

        response = self.c.get(reverse('core:product', args=['verity']))
        self.assertEqual(response.status_code, 200)

    def test_order_summary_view(self):
        #https://stackoverflow.com/questions/63054997/difference-between-user-objects-create-user-vs-user-objects-create-vs-user
        #I just found the solution, User.create.... and User.create_user
        #self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        self.c.login(username='john', password='johnpassword')
        response = self.c.get(reverse('core:order-summary'), follow=True)
        print(response.content)
        self.assertTemplateUsed('order-summary.html')


