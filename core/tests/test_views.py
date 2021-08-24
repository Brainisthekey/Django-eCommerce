from django.contrib.auth.models import User
from django.http.request import HttpRequest
from core.views import SearchResult
from django.test import TestCase, Client
from django.test.client import RequestFactory
from django.urls import reverse
from core.models import Item, Order, Adress, Coupon, OrderItem
from django.utils import timezone
from unittest import mock


class TestViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up all static models"""
        cls.coupon = Coupon.objects.create(code="test", amount=5)
        cls.user = User.objects.create(username="test")
        cls.user.set_password("testpassword")
        cls.user.save()
        cls.c = Client()
        cls.c.login(username="test", password="testpassword")
        cls.item = Item.objects.create(
            title="test_product",
            price=20,
            discount_price=15,
            description="test_description",
            category="R",
            lable="P",
            slug="verity",
            image="test",
        )
        cls.adress = Adress.objects.create(
            user=cls.user,
            street_adress="test",
            apartment_adress="test",
            country="Ukraine",
            zip="test",
            adress_type="B",
            default=True,
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
            quantity=1, ordered=False, item=cls.item, user=cls.user
        )
        cls.order.items.add(cls.order_item)

    def test_url_allowed_hosts_home_page(self):
        """Test connection to home page"""
        response = self.c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home-page.html")

    def test_home_page_html(self):
        """Test home page context"""
        response = self.c.get("/")
        html = response.content.decode("utf-8")
        self.assertIn("test_product", html)
        self.assertIn("5.0", html)
        self.assertIn("R", html)
        self.assertIn("P", html)
        self.assertIn("verity", html)
        self.assertIn("test", html)

    def test_url_allowed_hosts_product_page(self):
        """Test the Product page"""
        response = self.c.get(reverse("core:product", args=["verity"]))
        html = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "product-page.html")
        self.assertIn("test_product", html)

    def test_order_summary_view(self):
        """Test the Order Summary page"""
        response = self.c.get(reverse("core:order-summary"), follow=True)
        html = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "order-summary.html")

        # Assert for regular price
        self.assertIn("$20.0", html)

        # Assert for discount price
        self.assertIn("$15.0", html)

        # Assert for total price
        self.assertIn("$10.0", html)

        # Assert for coupon
        self.assertIn("$5.0", html)

        # Assert for quantity
        self.assertIn("1", html)

    def test_checkout_view(self):
        """Test Checkout page"""
        response = self.c.get(reverse("core:checkout"), follow=True)
        html = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "checkout-page.html")

        # Assert for title and quantity
        self.assertIn("<b>1</b> x test_product", html)

        # Assert for total price
        self.assertIn("$10.0", html)

    def test_views_if_order_is_deleted(self):
        """
        Test for Checkout and Order Summary view
        If order has been deleted
        """
        self.order.delete()
        self.order_item.delete()
        response = self.c.get(reverse("core:checkout"), follow=True)
        html = response.content.decode("utf-8")

        # Assert error when try to go at the Checkout page without active order
        self.assertIn("You do not have an active order", html)

        response = self.c.get(reverse("core:order-summary"), follow=True)
        html = response.content.decode("utf-8")

        # Assert error when try to go at the Order Summary page without active order
        self.assertIn("Your shopping cart is empty", html)

# Testing logic in View

    @mock.patch("core.views.add_and_save_coupon_to_the_order")
    @mock.patch("core.views.get_coupon")
    @mock.patch("core.views.check_user_for_active_coupon")
    @mock.patch("core.views.get_order_objects")
    @mock.patch("core.views.CouponForm")
    def test_add_coupon_view(
        self,
        mock_coupon_form,
        mock_get_order_object,
        mock_check_user,
        mock_get_coupon,
        mock_add_and_save_coupon,
    ):
        """Test for AddCouponView"""

        def send_post_add_coupon_request():
            response = self.c.post(
                reverse("core:add-coupon"), follow=True, data={"code": "test_coupon"}
            )
            return response.content.decode("utf-8")

        # #Situation where User pass incorect date in form - invalid form
        mock_coupon_form.return_value = mock.Mock(**{"is_valid.return_value": None})
        self.assertIn("You do not have an active order", send_post_add_coupon_request())

        # Situation where User has an active coupon
        mock_coupon_form.return_value = mock.Mock(
            **{
                "is_valid.return_value": "test_success_validation",
                "cleaned_data.get.return_value": "test_coupon",
            }
        )
        mock_get_order_object.return_value = "test_order"
        mock_check_user.return_value = "user_has_active_coupon"

        # Assert that Response which we get from page are correct
        self.assertIn(
            "You can not use one coupon two times", send_post_add_coupon_request()
        )

        # Situation where User does not have an active coupon
        mock_check_user.return_value = None
        mock_get_coupon.return_value = "test_get_success"
        mock_add_and_save_coupon.return_value = "test_add_and_save_coupon"

        # Assert that Response which we get from page are correct
        self.assertIn(
            "This coupon was successfully added to your order",
            send_post_add_coupon_request(),
        )

        # Situation where User provide a not existent coupon or validation error
        mock_get_coupon.return_value = None

        # Assert that Response which we get from page are correct
        self.assertIn("Coupon validation error", send_post_add_coupon_request())

    # My templates with filtering are the same
    # I mean that if Romance, Education and Buiseness view has changed only URL
    # And I want to be DRY, and write test for this 3 template in one place

    @mock.patch("core.views.filtering_items_by_caegories")
    def test_filtering_books(self, mock_filtering_items):
        """Testing RomanceView"""

        def send_get_request_to_filtered_home_page(path, context):
            response = self.c.get(
                reverse(f"core:{path}"), data={"items": context}, follow=True
            )
            return response.content.decode("utf-8")

        # Get context to pass into teplate
        mock_items = mock.Mock(
            **{
                "image.url": "test_image",
                "get_absolute_url": "test_path",
                "get_category_display": "test_category",
                "title": "test_title",
                "discount_price": "test_price",
            }
        )
        mock_filtering_items.return_value = [mock_items]

        # Iteration by verios path
        for response_html in [
            send_get_request_to_filtered_home_page(path="romance", context=mock_filtering_items),
            send_get_request_to_filtered_home_page(path="education-reference", context=mock_filtering_items),
            send_get_request_to_filtered_home_page(path="business-investing", context=mock_filtering_items),
        ]:
            # Assert rendering template
            self.assertIn("test_title", response_html)
            self.assertIn("test_category", response_html)
            self.assertIn("test_price", response_html)
            self.assertIn("test_path", response_html)
            self.assertIn("test_image", response_html)
            
    @mock.patch('core.views.filtering_items_by_icontains_filter')
    def test_search_result(self, mock_filtering_items):
        """Test SearchResultView"""

        #Mocking request.get
        mock_request_get = mock.Mock(
            **{
                'GET.get.return_value': 'test_item'
            }
        )
        mock_filtering_items.return_value = 'test_returned_item'

        #Assert that fucntion retturn corret item
        self.assertEqual(SearchResult.get_queryset(mock_request_get), 'test_returned_item')

        #Assert that query return the correct value
        self.assertEqual(mock_request_get.GET.get('q'), 'test_item')

        # request = RequestFactory().get('/search/?q=test_product')
        # self.assertEqual(SearchResult.get_queryset(), 'test_item')



class TestViewsAnonimousUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up a static client"""
        cls.c = Client()

    def test_checkout_view_non_auth(self):
        """Test Checkout view for anonymous user"""
        response = self.c.get(reverse("core:checkout"))

        # Assert status code for redirect
        self.assertEqual(response.status_code, 302)

        # Assert redirect to the right page
        response = self.c.get(reverse("core:checkout"), follow=True)
        self.assertTemplateUsed(response, "account/login.html")

    def test_order_summary_non_auth(self):
        """Test Order Summary view for anonymous user"""
        response = self.c.get(reverse("core:order-summary"))

        # Check status code for redirect
        self.assertEqual(response.status_code, 302)

        # Assert redirect to the right page
        response = self.c.get(reverse("core:checkout"), follow=True)
        self.assertTemplateUsed(response, "account/login.html")
