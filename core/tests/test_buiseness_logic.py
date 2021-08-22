from core.services.business_logic import get_information_about_order, convert_order_items_into_string_view, check_option_set_default, check_option_set_default, validate_and_create_a_new_adress, default_shipping_adress
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

    @mock.patch('core.services.business_logic.change_status_default_address')
    @mock.patch('core.services.business_logic.filter_and_check_default_adress')
    def test_check_option_set_default(self, mock_filter, mock_change_status):
        """
         Test the various options:
         Enabled options default adress or not
        """
        mock_filter.return_value = 'test'
        mock_change_status.return_value = 'test_if_not_default_shipping'

        #Assert if user doesn't have a default shipping adress
        self.assertEqual(check_option_set_default(set_default_shipping=None, shipping_adress='test', user='test', adress_type='S'), 'test_if_not_default_shipping')
        
        #Assert function call with the correct params
        mock_change_status.assert_called_with(address='test', status=True)

        #Assert if user has a default shipping adress
        mock_change_status.return_value = 'test_if_default_shipping'
        self.assertEqual(check_option_set_default(set_default_shipping='test', shipping_adress='test', user='test', adress_type='S'), 'test_if_default_shipping')

        #Assert function call with the correct params
        mock_change_status.assert_called_with('test', status=False)



    #Actually this doesn't work, because I had a nad patch to mock!

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
    @mock.patch('core.services.business_logic.add_shipping_adress_to_the_order')
    @mock.patch('core.services.business_logic.create_a_new_address')
    @mock.patch('core.services.business_logic.check_adress_by_street_adress')
    @mock.patch('core.services.business_logic.validate_from_for_whitespaces')
    def test_validate_and_create_a_new_adress(
            self,
            mock_validate_form,
            mock_check_adress,
            mock_create_new,
            mock_add_shipping,
            mock_check_option
        ):
        """
        Test validation form 
        and adding shipping adress to the order
        """
        #Situation when we don't have billing adress and create a new one
        mock_validate_form.return_value = 'success_validation'
        mock_check_adress.return_value = None
        mock_create_new.return_value = 'test_created_new_adress'
        mock_add_shipping.return_value = 'test_add_shipping'
        mock_check_option.return_value = 'test_check_option'

        #Assert that adress created successfully
        self.assertEqual(validate_and_create_a_new_adress(
            user='test_user',
            order='test_order',
            set_default_shipping='test_default',
            shipping_address1='test_shipping1',
            shipping_address2='test_shipping2',
            shipping_country='test_country',
            shipping_zip='test_zip',
            adress_type='test_adress_type'
        ), 'test_created_new_adress')

        #Situation when user does not provide all fields
        mock_validate_form.return_value = None

        #Assert error what occured
        self.assertEqual(validate_and_create_a_new_adress(
            user='test_user',
            order='test_order',
            set_default_shipping='test_default',
            shipping_address1='test_shipping1',
            shipping_address2='test_shipping2',
            shipping_country='test_country',
            shipping_zip='test_zip',
            adress_type='test_adress_type'
        ), 'Please fill in all required fields')






    @mock.patch('core.services.business_logic.validate_and_create_a_new_adress')
    @mock.patch('core.services.business_logic.check_enabled_option_use_default_shipping')
    @mock.patch('core.services.business_logic.filter_and_check_default_adress')
    def test_default_shipping_adress(self, mock_filter_and_check, mock_enabled_default, mock_validate_and_create
    ):
        """
        Test logic where:
            Adding shipping adress to the order,
            If enabled options "save as default"
            Adding this adress to the default adresses
        """
        #Situation when user have disabled option 'set as default'
        mock_filter_and_check.return_value = 'test_existing_default'
        mock_enabled_default.return_value = 'User do not have enabled option save as default'
        mock_validate_and_create.return_value = 'test_validated_and_created'

        #Assert that Adress pass validation and has been created
        self.assertEqual(default_shipping_adress(
            user='test_user',
            order='test_order',
            use_default_shipping='test_default_shipping',
            set_default_shipping='test_set_default_shipping',
            shipping_address1='test_shipping_adress1',
            shipping_address2='test_shipping_adress2',
            shipping_country='test_shipping_country',
            shipping_zip='test_shipping_zip',
            adress_type='test_adress_type'
        ), 'test_validated_and_created')

        #Situation when user has enabled option 'use default adress'
        mock_enabled_default.return_value = 'Successfully added to the order'

        #Assert that User used a default adress
        self.assertEqual(default_shipping_adress(
            user='test_user',
            order='test_order',
            use_default_shipping='test_default_shipping',
            set_default_shipping='test_set_default_shipping',
            shipping_address1='test_shipping_adress1',
            shipping_address2='test_shipping_adress2',
            shipping_country='test_shipping_country',
            shipping_zip='test_shipping_zip',
            adress_type='test_adress_type'
        ), 'User use the default shipping adress')

        #Situation when user entry adress manually and has validation error
        mock_enabled_default.return_value = 'validation_error'

        #Assrt that Error has been occured
        self.assertEqual(default_shipping_adress(
            user='test_user',
            order='test_order',
            use_default_shipping='test_default_shipping',
            set_default_shipping='test_set_default_shipping',
            shipping_address1='test_shipping_adress1',
            shipping_address2='test_shipping_adress2',
            shipping_country='test_shipping_country',
            shipping_zip='test_shipping_zip',
            adress_type='test_adress_type'
        ), 'Please fill in the required shipping address fields')

        


