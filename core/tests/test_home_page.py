from django.test import TestCase


class TestHomePageURL(TestCase):

    #Add test for all connections
    def test_url_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


         
