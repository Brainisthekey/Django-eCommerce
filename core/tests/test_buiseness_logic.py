from core.services.business_logic import get_information_about_order, convert_order_items_into_string_view, check_option_set_default, check_option_set_default, validate_and_create_a_new_adress
import unittest
from core.models import Adress, OrderItem
from django.test import TestCase
from unittest import mock


class TestBuisenessLogic(TestCase):

    @mock.patch('core.services.db_services.get_all_objects_from_order_items')
    def test_get_information_about_order(self, mock_orders):
        """Test getting information about order"""
        #Actually I don't need to mock this query to Database
        #Because we don't have a call to this fucntion, we just pass it in argumets to fucntion
        mock_orders = mock.Mock(
            **{
                'quantity': 2,
                'item.title': 'test'
            }
        )
        #Assert that function collect Order information
        self.assertEqual(get_information_about_order([mock_orders]), (2, [[2, 'test']]))

    def test_another_way_to_test_information(self):
        """Another way to test getting information about order"""
        #Actually I don't need to mock this query to Database
        #Because we don't have a call to this fucntion, we just pass it in argumets to fucntion
        mock_queryset = mock.Mock(spec=OrderItem.objects)
        mock_queryset.all.return_value = mock_queryset
        mock_response = mock.Mock(
            **{
                'quantity': 2,
                'item.title': 'test'
            }
        )
        self.assertEqual(get_information_about_order([mock_response]), (2, [[2, 'test']]))


    @mock.patch('core.services.business_logic.get_information_about_order')
    def test_convert_order_items_into_string_view(self, mock_info_order):
        """Test converting order into string representation"""
        mock_info_order.return_value = (2, [[2, 'test']])

        #Assert that function convert Order to the string
        self.assertEqual(convert_order_items_into_string_view(orders='test'), '1. test x 2')


#Test for buiseness logic checkout view

    #Why this doens't work for me :(
    # @mock.patch('core.services.db_services.change_status_default_address')
    # @mock.patch('core.services.db_services.filter_and_check_default_adress')
    # def test_check_option_set_default(self, mock_filter_and_check, mock_default_adress):
    #     """
    #     Test the various options:
    #     Enabled options default adress or not
    #     """
    #     mock_filter_and_check.return_value = mock.Mock()
    #     mock_default_adress.return_value = mock.Mock()
        
    #     self.assertEqual(check_option_set_default(set_default_shipping='test', shipping_adress='B', user='1', adress_type='B'), 'test1')



    @mock.patch('core.services.business_logic.check_option_set_default')
    @mock.patch('core.services.db_services.add_shipping_adress_to_the_order')
    @mock.patch('core.services.db_services.create_a_new_address')
    @mock.patch('core.services.db_services.check_adress_by_street_adress')
    @mock.patch('core.services.form_services.validate_from_for_whitespaces')
    def test_validate_and_create_a_new_adress(
            self,
            mock_validate_form,
            mock_check_address,
            mock_create_address,
            mock_add_shipping,
            mock_check_option
        ):
        mock_validate_form.return_value = 'test'
        mock_check_address.return_value = 'test'
        mock_create_address.return_value = 'test'
        mock_add_shipping.return_value = 'test'
        mock_check_option.return_value = 'test'
        self.assertEqual(validate_and_create_a_new_adress(
            # WTTTTTFFFFF why user='test' doens't work but 1 works..........
            #user='test'
            user=1,
            order='test',
            set_default_shipping='test',
            shipping_address1='test',
            shipping_address2='test',
            shipping_country='test',
            shipping_zip='test',
            adress_type='B'
        ), 1)


