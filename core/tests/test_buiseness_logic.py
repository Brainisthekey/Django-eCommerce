from core.services.business_logic import get_information_about_order, convert_order_items_into_string_view, check_option_set_default, check_option_set_default, validate_and_create_a_new_adress, default_shipping_adress, check_enabled_option_use_default_shipping, check_default_shipping_adress, filtered_billing_adress_and_create_new, check_option_default_shipping, change_status_default_adress_if_not_exist
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

    @mock.patch('core.services.business_logic.check_default_shipping_adress')
    def test_check_enabled_option_use_default_shipping(self, mock_check_default_shipping):
        """Test checking enabled options - use defalt shipping adress"""
        
        #Situation when user use default shipping address
        mock_check_default_shipping.return_value = 'User use the default shipping adress'

        #Assert output user use default shipping adress
        self.assertEqual(check_enabled_option_use_default_shipping(
            use_default_shipping='test_enable_default_shipping',
            address_shipping_queryset='test_queryset',
            order='test_order'
        ), 'User use the default shipping adress')
        
        #Assert when user has not enable option - use default
        self.assertEqual(check_enabled_option_use_default_shipping(
            use_default_shipping=None,
            address_shipping_queryset='test_queryset',
            order='test_order'
        ), 'User do not have enabled option save as default')

    @mock.patch('core.services.business_logic.add_shipping_adress_to_the_order')
    def test_check_default_shipping_adress(self, mock_adding_to_the_order):
        """
        Test existens of the default shipping adress
        Else - error message
        """

        #Situation when adress queryset exist
        mock_adding_to_the_order.return_value = 'Successfully added to the order'

        #Assert that shipping adress succesffully added to the order
        self.assertEqual(check_default_shipping_adress(
            order='test_order',
            address_shipping_queryset='test_adress_queryset'
        ), 'Successfully added to the order')

        #Assert situation when adress_shipping_queryset does not exist
        self.assertEqual(check_default_shipping_adress(
            order='test_order',
            address_shipping_queryset=None
        ), 'Queryset does not exist')

#Testing logic for enabled and disabled option - "the same billing and shipping"

    @mock.patch('core.services.business_logic.add_billing_address_to_the_order')
    @mock.patch('core.services.business_logic.change_status_default_address')
    @mock.patch('core.services.business_logic.filter_and_check_default_adress')
    @mock.patch('core.services.business_logic.create_a_new_address')
    @mock.patch('core.services.business_logic.check_adress_by_street_adress')
    def test_filtered_billing_adress_and_create_new(
            self,
            mock_check_adress,
            mock_create_new,
            mock_filter_and_ckeck_default,
            mock_change_status_default,
            mock_add_billing_to_order
        ):
        """
        Test this layer of logic:
            -Filtering billing adress if not exists then create
            -If user has default billing adress, and enable option 'save as default'
            -Change status the default adress
        """

        #Situation when adress does not exist in database
        mock_check_adress.return_value = None
        mock_create_new.return_value = 'test_created_a_new_one'
        mock_filter_and_ckeck_default.return_value = 'test_default_billing_exist'
        mock_change_status_default.return_value = 'test_change_status_default_adress'
        mock_add_billing_to_order.return_value = 'add billing_to_the_order'

        self.assertEqual(filtered_billing_adress_and_create_new(
            user='test_user',
            order='test_order',
            set_default_billing='test_default_billing',
            billing_address1='test_billing_address1',
            shipping_address1='test_shipping_address1',
            shipping_address2='test_shipping_address2',
            shipping_country='test_shipping_country',
            shipping_zip='test_shipping_zip'
        ), 'Created a new billing adress')

        #Check that function change_status_default_aderss was called two times
        self.assertEqual(mock_change_status_default.call_count, 2)

        #Check that function has called with the correct params
        mock_change_status_default.assert_has_calls([
            mock.call(address='test_default_billing_exist', status=False),
            mock.call(address='test_created_a_new_one', status=True)
        ])
        
        #Check that fucntion add billing adress to the order has called with correct params
        mock_add_billing_to_order.assert_called_with(order='test_order', adress_queryset='test_created_a_new_one')

        #Situation when adress exist
        mock_check_adress.return_value = 'test_with_exist_adress'

        #Assert occured message that adress exist
        self.assertEqual(filtered_billing_adress_and_create_new(
            user='test_user',
            order='test_order',
            set_default_billing='test_default_billing',
            billing_address1='test_billing_address1',
            shipping_address1='test_shipping_address1',
            shipping_address2='test_shipping_address2',
            shipping_country='test_shipping_country',
            shipping_zip='test_shipping_zip'
        ), 'Adress exists')

    @mock.patch('core.services.business_logic.filtered_billing_adress_and_create_new')
    @mock.patch('core.services.business_logic.add_billing_address_to_the_order')
    def test_check_option_default_shipping(self, mock_add_billing, mock_filtered_and_create):
        """
        Test enabled option - use default shipping address
        Else check if this adress exist or create a new one
        """

        #Situation when user enable option to use the default shipping address
        mock_add_billing.return_value = 'test_added_billing_adress'
        mock_filtered_and_create.return_value = 'test_created_billing_address'

        #Assert that current billing address has been added to the order
        self.assertEqual(check_option_default_shipping(
            user='test_user',
            order='test_order',
            use_default_shipping='test_default_shipping',
            billing_adress1='test_billing_address1',
            shipping_address1='shipping_address1',
            shipping_address2='shipping_address2',
            shipping_country='shipping_country',
            shipping_zip='shipping_zip',
            set_default_billing='set_default_billing',
            address_shipping_queryset='address_shipping_queryset'
        ), 'Added billing adress to the Order')

        #Assert situation when user disable option - use default_shipping
        self.assertEqual(check_option_default_shipping(
            user='test_user',
            order='test_order',
            #This params has been changed
            use_default_shipping=None,
            billing_adress1='test_billing_address1',
            shipping_address1='shipping_address1',
            shipping_address2='shipping_address2',
            shipping_country='shipping_country',
            shipping_zip='shipping_zip',
            set_default_billing='set_default_billing',
            address_shipping_queryset='address_shipping_queryset'
        ), 'test_created_billing_address')

    @mock.patch('core.services.business_logic.change_status_default_address')
    @mock.patch('core.services.business_logic.create_a_new_address')
    @mock.patch('core.services.business_logic.check_adress_by_street_adress')
    def test_change_status_default_adress_if_not_exist(
            self,
            mock_check_adress,
            mock_create_a_new,
            mock_change_status_default
        ):
        """Test changing the default adress if not exists"""

        #Situation when adress exists in database
        mock_check_adress.return_value = 'test_check_adress'
        mock_create_a_new.return_value = 'test_create_a_new_one'
        mock_change_status_default.return_value = 'test_change_status_default'
        mock_address_shipping_queryset = mock.Mock(
            **{
                'street_adress': 'test_street_adress',
                'apartment_adress': 'test_apartment_adress',
                'country': 'test_country',
                'zip': 'test_zip'
            }
        )
        #Assert that default address has been chaned to existent one
        self.assertEqual(change_status_default_adress_if_not_exist(
            user='test_user',
            address_shipping_queryset=mock_address_shipping_queryset
        ), 'Default address has been chaned to existent one')

        #Situation when adress does not exists in database
        mock_check_adress.return_value = None

        #Assert that default adress has been changed to new
        self.assertEqual(change_status_default_adress_if_not_exist(
            user='test_user',
            address_shipping_queryset=mock_address_shipping_queryset
        ), 'Default adress has been changed to new')

    

    