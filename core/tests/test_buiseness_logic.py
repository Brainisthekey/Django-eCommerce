from core.services.business_logic import (
    get_information_about_order,
    convert_order_items_into_string_view,
    check_option_set_default,
    check_option_set_default,
    validate_and_create_a_new_adress,
    default_shipping_adress,
    check_enabled_option_use_default_shipping,
    check_default_shipping_adress,
    filtered_billing_adress_and_create_new,
    check_option_default_shipping,
    change_status_default_adress_if_not_exist,
    comprare_shipping_and_billing_adresses,
    check_adress_billing_quresytet,
    check_set_default_shipping_adress,
    the_same_billing_logic,
    disabled_billing_and_default_logic,
    create_delivered_object_item,
    delete_order_and_order_items,
)
from core.models import Adress, OrderItem
from django.test import TestCase
from unittest import mock


class TestBuisenessLogic(TestCase):
    @mock.patch("core.services.db_services.get_all_objects_from_order_items")
    def test_get_information_about_order(self, mock_orders):
        """Test getting information about order"""

        # Actually I don't need to mock this query to Database
        # Because we don't have a call to this fucntion, we just pass it in argumets to fucntion
        mock_orders = mock.Mock(**{"quantity": 2, "item.title": "test"})
        # Assert that function collect Order information
        self.assertEqual(get_information_about_order([mock_orders]), (2, [[2, "test"]]))

    def test_another_way_to_test_information(self):
        """Another way to test getting information about order"""

        # Actually I don't need to mock this query to Database
        # Because we don't have a call to this fucntion, we just pass it in argumets to fucntion
        mock_queryset = mock.Mock(spec=OrderItem.objects)
        mock_queryset.all.return_value = mock_queryset
        mock_response = mock.Mock(**{"quantity": 2, "item.title": "test"})
        self.assertEqual(
            get_information_about_order([mock_response]), (2, [[2, "test"]])
        )

    @mock.patch("core.services.business_logic.get_information_about_order")
    def test_convert_order_items_into_string_view(self, mock_info_order):
        """Test converting order into string representation"""
        mock_info_order.return_value = (2, [[2, "test"]])

        # Assert that function convert Order to the string
        self.assertEqual(
            convert_order_items_into_string_view(orders="test"), "1. test x 2"
        )

    # Test for buiseness logic checkout view

    @mock.patch("core.services.business_logic.change_status_default_address")
    @mock.patch("core.services.business_logic.filter_and_check_default_adress")
    def test_check_option_set_default(self, mock_filter, mock_change_status):
        """
        Test the various options:
        Enabled options default adress or not
        """

        mock_filter.return_value = "test"
        mock_change_status.return_value = "test_if_not_default_shipping"

        # Assert if user doesn't have a default shipping adress
        self.assertEqual(
            check_option_set_default(
                set_default_shipping=None,
                shipping_adress="test",
                user="test",
                adress_type="S",
            ),
            "test_if_not_default_shipping",
        )

        # Assert function call with the correct params
        mock_change_status.assert_called_with(address="test", status=True)

        # Assert if user has a default shipping adress
        mock_change_status.return_value = "test_if_default_shipping"
        self.assertEqual(
            check_option_set_default(
                set_default_shipping="test",
                shipping_adress="test",
                user="test",
                adress_type="S",
            ),
            "test_if_default_shipping",
        )

        # Assert function call with the correct params
        mock_change_status.assert_called_with("test", status=False)

    # Actually this doesn't work, because I had a bad patch to mock!

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

    @mock.patch("core.services.business_logic.check_option_set_default")
    @mock.patch("core.services.business_logic.add_shipping_adress_to_the_order")
    @mock.patch("core.services.business_logic.create_a_new_address")
    @mock.patch("core.services.business_logic.check_adress_by_street_adress")
    @mock.patch("core.services.business_logic.validate_from_for_whitespaces")
    def test_validate_and_create_a_new_adress(
        self,
        mock_validate_form,
        mock_check_adress,
        mock_create_new,
        mock_add_shipping,
        mock_check_option,
    ):
        """
        Test validation form
        and adding shipping adress to the order
        """

        # Situation when we don't have billing adress and create a new one
        mock_validate_form.return_value = "success_validation"
        mock_check_adress.return_value = None
        mock_create_new.return_value = "test_created_new_adress"
        mock_add_shipping.return_value = "test_add_shipping"
        mock_check_option.return_value = "test_check_option"

        # Assert that adress created successfully
        self.assertEqual(
            validate_and_create_a_new_adress(
                user="test_user",
                order="test_order",
                set_default_shipping="test_default",
                shipping_address1="test_shipping1",
                shipping_address2="test_shipping2",
                shipping_country="test_country",
                shipping_zip="test_zip",
                adress_type="test_adress_type",
            ),
            "test_created_new_adress",
        )

        # Situation when user does not provide all fields
        mock_validate_form.return_value = None

        # Assert error what occured
        self.assertEqual(
            validate_and_create_a_new_adress(
                user="test_user",
                order="test_order",
                set_default_shipping="test_default",
                shipping_address1="test_shipping1",
                shipping_address2="test_shipping2",
                shipping_country="test_country",
                shipping_zip="test_zip",
                adress_type="test_adress_type",
            ),
            "Please fill in all required fields",
        )

    @mock.patch("core.services.business_logic.validate_and_create_a_new_adress")
    @mock.patch("core.services.business_logic.check_enabled_option_use_default_shipping")
    @mock.patch("core.services.business_logic.filter_and_check_default_adress")
    def test_default_shipping_adress(
        self, mock_filter_and_check, mock_enabled_default, mock_validate_and_create
    ):
        """
        Test logic where:
            Adding shipping adress to the order,
            If enabled options "save as default"
            Adding this adress to the default adresses
        """

        # Situation when user have disabled option 'set as default'
        mock_filter_and_check.return_value = "test_existing_default"
        mock_enabled_default.return_value = (
            "User do not have enabled option save as default"
        )
        mock_validate_and_create.return_value = "test_validated_and_created"

        # Assert that Adress pass validation and has been created
        self.assertEqual(
            default_shipping_adress(
                user="test_user",
                order="test_order",
                use_default_shipping="test_default_shipping",
                set_default_shipping="test_set_default_shipping",
                shipping_address1="test_shipping_adress1",
                shipping_address2="test_shipping_adress2",
                shipping_country="test_shipping_country",
                shipping_zip="test_shipping_zip",
                adress_type="test_adress_type",
            ),
            "test_validated_and_created",
        )

        # Situation when user has enabled option 'use default adress'
        mock_enabled_default.return_value = "Successfully added to the order"

        # Assert that User used a default adress
        self.assertEqual(
            default_shipping_adress(
                user="test_user",
                order="test_order",
                use_default_shipping="test_default_shipping",
                set_default_shipping="test_set_default_shipping",
                shipping_address1="test_shipping_adress1",
                shipping_address2="test_shipping_adress2",
                shipping_country="test_shipping_country",
                shipping_zip="test_shipping_zip",
                adress_type="test_adress_type",
            ),
            "User use the default shipping adress",
        )

        # Situation when user entry adress manually and has validation error
        mock_enabled_default.return_value = "validation_error"

        # Assrt that Error has been occured
        self.assertEqual(
            default_shipping_adress(
                user="test_user",
                order="test_order",
                use_default_shipping="test_default_shipping",
                set_default_shipping="test_set_default_shipping",
                shipping_address1="test_shipping_adress1",
                shipping_address2="test_shipping_adress2",
                shipping_country="test_shipping_country",
                shipping_zip="test_shipping_zip",
                adress_type="test_adress_type",
            ),
            "Please fill in the required shipping address fields",
        )

    @mock.patch("core.services.business_logic.check_default_shipping_adress")
    def test_check_enabled_option_use_default_shipping(
        self, mock_check_default_shipping
    ):
        """Test checking enabled options - use defalt shipping adress"""

        # Situation when user use default shipping address
        mock_check_default_shipping.return_value = (
            "User use the default shipping adress"
        )

        # Assert output user use default shipping adress
        self.assertEqual(
            check_enabled_option_use_default_shipping(
                use_default_shipping="test_enable_default_shipping",
                address_shipping_queryset="test_queryset",
                order="test_order",
            ),
            "User use the default shipping adress",
        )

        # Assert when user has not enable option - use default
        self.assertEqual(
            check_enabled_option_use_default_shipping(
                use_default_shipping=None,
                address_shipping_queryset="test_queryset",
                order="test_order",
            ),
            "User do not have enabled option save as default",
        )

    @mock.patch("core.services.business_logic.add_shipping_adress_to_the_order")
    def test_check_default_shipping_adress(self, mock_adding_to_the_order):
        """
        Test existens of the default shipping adress
        Else - error message
        """

        # Situation when adress queryset exist
        mock_adding_to_the_order.return_value = "Successfully added to the order"

        # Assert that shipping adress succesffully added to the order
        self.assertEqual(
            check_default_shipping_adress(
                order="test_order", address_shipping_queryset="test_adress_queryset"
            ),
            "Successfully added to the order",
        )

        # Assert situation when adress_shipping_queryset does not exist
        self.assertEqual(
            check_default_shipping_adress(
                order="test_order", address_shipping_queryset=None
            ),
            "Queryset does not exist",
        )

    # Testing logic for enabled and disabled option - "the same billing and shipping"

    @mock.patch("core.services.business_logic.add_billing_address_to_the_order")
    @mock.patch("core.services.business_logic.change_status_default_address")
    @mock.patch("core.services.business_logic.filter_and_check_default_adress")
    @mock.patch("core.services.business_logic.create_a_new_address")
    @mock.patch("core.services.business_logic.check_adress_by_street_adress")
    def test_filtered_billing_adress_and_create_new(
        self,
        mock_check_adress,
        mock_create_new,
        mock_filter_and_ckeck_default,
        mock_change_status_default,
        mock_add_billing_to_order,
    ):
        """
        Test this layer of logic:
            -Filtering billing adress if not exists then create
            -If user has default billing adress, and enable option 'save as default'
            -Change status the default adress
        """

        # Situation when adress does not exist in database
        mock_check_adress.return_value = None
        mock_create_new.return_value = "test_created_a_new_one"
        mock_filter_and_ckeck_default.return_value = "test_default_billing_exist"
        mock_change_status_default.return_value = "test_change_status_default_adress"
        mock_add_billing_to_order.return_value = "add billing_to_the_order"

        self.assertEqual(
            filtered_billing_adress_and_create_new(
                user="test_user",
                order="test_order",
                set_default_billing="test_default_billing",
                billing_address1="test_billing_address1",
                shipping_address1="test_shipping_address1",
                shipping_address2="test_shipping_address2",
                shipping_country="test_shipping_country",
                shipping_zip="test_shipping_zip",
            ),
            "Created a new billing adress",
        )

        # Check that function change_status_default_aderss was called two times
        self.assertEqual(mock_change_status_default.call_count, 2)

        # Check that function has called with the correct params
        mock_change_status_default.assert_has_calls(
            [
                mock.call(address="test_default_billing_exist", status=False),
                mock.call(address="test_created_a_new_one", status=True),
            ]
        )

        # Check that fucntion add billing adress to the order has called with correct params
        mock_add_billing_to_order.assert_called_with(
            order="test_order", adress_queryset="test_created_a_new_one"
        )

        # Situation when adress exist
        mock_check_adress.return_value = "test_with_exist_adress"

        # Assert occured message that adress exist
        self.assertEqual(
            filtered_billing_adress_and_create_new(
                user="test_user",
                order="test_order",
                set_default_billing="test_default_billing",
                billing_address1="test_billing_address1",
                shipping_address1="test_shipping_address1",
                shipping_address2="test_shipping_address2",
                shipping_country="test_shipping_country",
                shipping_zip="test_shipping_zip",
            ),
            "Adress exists",
        )

    @mock.patch("core.services.business_logic.filtered_billing_adress_and_create_new")
    @mock.patch("core.services.business_logic.add_billing_address_to_the_order")
    def test_check_option_default_shipping(
        self, mock_add_billing, mock_filtered_and_create
    ):
        """
        Test enabled option - use default shipping address
        Else check if this adress exist or create a new one
        """

        # Situation when user enable option to use the default shipping address
        mock_add_billing.return_value = "test_added_billing_adress"
        mock_filtered_and_create.return_value = "test_created_billing_address"

        # Assert that current billing address has been added to the order
        self.assertEqual(
            check_option_default_shipping(
                user="test_user",
                order="test_order",
                use_default_shipping="test_default_shipping",
                billing_adress1="test_billing_address1",
                shipping_address1="shipping_address1",
                shipping_address2="shipping_address2",
                shipping_country="shipping_country",
                shipping_zip="shipping_zip",
                set_default_billing="set_default_billing",
                address_shipping_queryset="address_shipping_queryset",
            ),
            "Added billing adress to the Order",
        )

        # Assert situation when user disable option - use default_shipping
        self.assertEqual(
            check_option_default_shipping(
                user="test_user",
                order="test_order",
                # This params has been changed
                use_default_shipping=None,
                billing_adress1="test_billing_address1",
                shipping_address1="shipping_address1",
                shipping_address2="shipping_address2",
                shipping_country="shipping_country",
                shipping_zip="shipping_zip",
                set_default_billing="set_default_billing",
                address_shipping_queryset="address_shipping_queryset",
            ),
            "test_created_billing_address",
        )

    @mock.patch("core.services.business_logic.change_status_default_address")
    @mock.patch("core.services.business_logic.create_a_new_address")
    @mock.patch("core.services.business_logic.check_adress_by_street_adress")
    def test_change_status_default_adress_if_not_exist(
        self, mock_check_adress, mock_create_a_new, mock_change_status_default
    ):
        """Test changing the default adress if not exists"""

        # Situation when adress exists in database
        mock_check_adress.return_value = "test_check_adress"
        mock_create_a_new.return_value = "test_create_a_new_one"
        mock_change_status_default.return_value = "test_change_status_default"
        mock_address_shipping_queryset = mock.Mock(
            **{
                "street_adress": "test_street_adress",
                "apartment_adress": "test_apartment_adress",
                "country": "test_country",
                "zip": "test_zip",
            }
        )
        # Assert that default address has been chaned to existent one
        self.assertEqual(
            change_status_default_adress_if_not_exist(
                user="test_user",
                address_shipping_queryset=mock_address_shipping_queryset,
            ),
            "Default address has been chaned to existent one",
        )

        # Situation when adress does not exists in database
        mock_check_adress.return_value = None

        # Assert that default adress has been changed to new
        self.assertEqual(
            change_status_default_adress_if_not_exist(
                user="test_user",
                address_shipping_queryset=mock_address_shipping_queryset,
            ),
            "Default adress has been changed to new",
        )

    @mock.patch("core.services.business_logic.change_status_default_adress_if_not_exist")
    @mock.patch("core.services.business_logic.change_status_default_address")
    def test_comprare_shipping_and_billing_adresses(
        self, mock_change_status, mock_change_status_not_exist
    ):
        """
        Test the logic:
            -Compare shipping and billing adress
            -Change the status of default adress if different adresses
            -Change the status of default adress if not exists
        """

        # Situation when address_shipping_queryset not equal address_billing_queryset
        mock_change_status.return_value = "test_change_status_default"
        mock_change_status_not_exist.return_value = (
            "test_change_status_default_if_not_exist_in_db"
        )
        mock_address_shipping = mock.Mock(street_adress="test_shipping_street_address")
        mock_address_billing = mock.Mock(street_adress="test_billing_street_address")
        comprare_shipping_and_billing_adresses(
            user="test_user",
            address_shipping_queryset=mock_address_shipping,
            address_billing_queryset=mock_address_billing,
        )
        # Assert that fucntion to change default adress has been called
        mock_change_status.assert_called_once()
        mock_change_status_not_exist.assert_called_once()

    @mock.patch("core.services.business_logic.change_status_default_adress_if_not_exist")
    @mock.patch("core.services.business_logic.comprare_shipping_and_billing_adresses")
    def test_check_adress_billing_quresytet(
        self, mock_comparing_adress, mock_change_status_if_not_exist
    ):
        """
        Test the logic:
            -Check billing address queryset
            -If exist call comparing function
            -Else change the status of default address
        """
        # Situation when address_billing_queryset does not exist
        mock_comparing_adress.return_value = "test_called_comparing_function"
        mock_change_status_if_not_exist.return_value = (
            "test_called_changing_default_adress"
        )

        check_adress_billing_quresytet(
            user="test_user",
            address_billing_queryset=None,
            address_shipping_queryset="test_shipping_address",
        )

        # Assert that function to change status order has been called
        mock_change_status_if_not_exist.assert_called_once()

        # Assert that comparing function has not been called
        mock_comparing_adress.assert_not_called()

        # Situation when address billing queryset exist
        check_adress_billing_quresytet(
            user="test_user",
            address_billing_queryset="test_billing_address",
            address_shipping_queryset="test_shipping_address",
        )

        # Assert that comparing function has been called
        mock_comparing_adress.assert_called_once()

    @mock.patch("core.services.business_logic.filtered_billing_adress_and_create_new")
    @mock.patch("core.services.business_logic.check_adress_billing_quresytet")
    def test_check_set_default_shipping_adress(
        self, mock_check_billing_address, mock_filter_and_create_new_billing
    ):
        """
        Test the logic:
            -Check option of default shipping adress
            -If enabled check adress billing queryset
            -Else filtering billing adress and create new
        """

        # Situation when User has enable option - set default billing
        mock_check_billing_address.return_value = "test_check_billing_queryset"
        mock_filter_and_create_new_billing.return_value = "test_filtered_and_created_one"
        mock_addres_shipping_queryset = mock.Mock(
            **{
                "street_adress": "test_street_adress",
                "apartment_adress": "test_apartment_adress",
                "country": "test_country",
                "zip": "test_zip",
            }
        )

        check_set_default_shipping_adress(
            user="test_user",
            order="test_order",
            address_shipping_queryset=mock_addres_shipping_queryset,
            set_default_billing="test_default_billing",
            address_billing_queryset="test_address_billing",
        )

        # Assert that fucntion to check adress billing queryset has been called
        mock_check_billing_address.assert_called_once()

        # Assert that filtering and creating a new adress fucntion has not been called
        mock_filter_and_create_new_billing.assert_not_called()

        # Situation when user does not have an active option - set default billing
        check_set_default_shipping_adress(
            user="test_user",
            order="test_order",
            address_shipping_queryset=mock_addres_shipping_queryset,
            set_default_billing=None,
            address_billing_queryset="test_address_billing",
        )

        # Assert that fucntion to filtering and createing a new address has been called
        mock_filter_and_create_new_billing.assert_called_once()

    @mock.patch("core.services.business_logic.check_set_default_shipping_adress")
    @mock.patch("core.services.business_logic.check_option_default_shipping")
    @mock.patch("core.services.business_logic.filter_and_check_default_adress")
    def test_the_same_billing_logic(
        self,
        mock_check_default_addresses,
        mock_check_option_def_shipping,
        mock_check_set_default_shipping,
    ):
        """
        Test the logic:
            -Billing address is the same as my shipping address
            -Save as default shipping address
            -Save as default billing address
        """
        mock_check_default_addresses.return_value = "test_address"
        mock_check_set_default_shipping.return_value = "test_set_as_default"
        mock_check_option_def_shipping.return_value = (
            "Added billing adress to the Order"
        )

        # Situation when User has disabled option - the same billing address
        the_same_billing_logic(
            user="test_user",
            order="test_order",
            same_billing_address=None,
            use_default_shipping="use_default_shipping",
            billing_adress1="billing_adress1",
            shipping_address1="shipping_address1",
            shipping_address2="shipping_address2",
            shipping_country="shipping_country",
            shipping_zip="shipping_zip",
            set_default_billing="set_default_billing",
        )

        # Assert that function check_option_default_shipping has not been called
        mock_check_option_def_shipping.assert_not_called()

        # Assert that function check_set_default_shipping_adress has not been called
        mock_check_set_default_shipping.assert_not_called()

        # Situation when User has enabled option - the same billing address
        the_same_billing_logic(
            user="test_user",
            order="test_order",
            same_billing_address="test_same_billing_address",
            use_default_shipping="use_default_shipping",
            billing_adress1="billing_adress1",
            shipping_address1="shipping_address1",
            shipping_address2="shipping_address2",
            shipping_country="shipping_country",
            shipping_zip="shipping_zip",
            set_default_billing="set_default_billing",
        )

        # Assert that function filtering_and_check_default_address has been called
        self.assertEqual(mock_check_default_addresses.call_count, 4)

        # Assert that function filtering_and_check_default_address had pass the correct params
        mock_check_default_addresses.assert_has_calls(
            [
                mock.call(user="test_user", adress_type="S"),
                mock.call(user="test_user", adress_type="B"),
            ]
        )

        # Assert that fucntion check_option_default_shipping has been called
        mock_check_option_def_shipping.assert_called_once()

        # Assert that function check_option_default_shipping has returned the correct response
        self.assertEqual(mock_check_option_def_shipping(), "Added billing adress to the Order")

        # Assert that fucntion check_set_default_shipping_adress has been called
        mock_check_set_default_shipping.assert_called_once()

# Testing logic for disabled both options:
#   Billing address is the same as my shipping address
#   Save as default billing address

    @mock.patch("core.services.business_logic.validate_and_create_a_new_adress")
    def test_disabled_billing_and_default_logic(self, mock_validate_and_create_new):
        """
        Test the logic where disabled both options:
            -Billing address is the same as my shipping address
            -Save as default shipping address
        """
        mock_validate_and_create_new.return_value = "test_validated_and_created_order"

        # Situation when user have enable one of two options
        self.assertEqual(
            disabled_billing_and_default_logic(
                user="test_user",
                order="order",
                same_billing_address="test_same_billing_address",
                use_default_billing=None,
                set_default_billing="test_set_default_billing",
                billing_address1="test_billing_address1",
                billing_address2="test_billing_address2",
                billing_country="test_billing_country",
                billing_zip="test_billing_zip",
                adress_type="test_adress_type",
            ),
            "Please fill in the required shipping address fields",
        )

        # Assert that function validate_and_create_a_new_adress was not called
        mock_validate_and_create_new.assert_not_called()

        # Situation when user have disabled the both options
        disabled_billing_and_default_logic(
            user="test_user",
            order="order",
            same_billing_address=None,
            use_default_billing=None,
            set_default_billing="test_set_default_billing",
            billing_address1="test_billing_address1",
            billing_address2="test_billing_address2",
            billing_country="test_billing_country",
            billing_zip="test_billing_zip",
            adress_type="test_adress_type",
        )

        # Assert that fucntion validate_and_create_a_new_adress has been called
        mock_validate_and_create_new.assert_called_once()

    # Testing logic for creating devilered object and delete order

    @mock.patch("core.services.business_logic.create_a_new_devilered_order_object")
    @mock.patch("core.services.business_logic.convert_order_items_into_string_view")
    @mock.patch("core.services.business_logic.get_information_about_order")
    @mock.patch("core.services.business_logic.get_all_objects_from_order_items")
    def test_create_delivered_object_item(
        self,
        mock_get_all_order_items,
        mock_get_info_order,
        mock_convert_order_into_string,
        mock_create_new_devilered_item,
    ):
        """Testing the logic for creating devilered object item"""
        mock_get_all_order_items.return_value = "test_get_all_order_items"
        mock_get_info_order.return_value = "1", "test_info_order"
        mock_convert_order_into_string.return_value = "test_convertation"
        mock_create_new_devilered_item.return_value = "test_create_item"

        create_delivered_object_item(user="test_user")

        # Assert that fucntion get_all_objects_from_order_items has been called
        mock_get_all_order_items.assert_called_once()

        # Assert that fucntion get_information_about_order has been called
        mock_get_info_order.assert_called_once()

        # Assert that fucntion convert_order_items_into_string_view has been called
        mock_convert_order_into_string.assert_called_once()

        # Assert that fucntion create_a_new_devilered_order_object has been called
        mock_create_new_devilered_item.assert_called_once()

    @mock.patch("core.services.business_logic.delete_order")
    @mock.patch("core.services.business_logic.delete_all_items_from_order")
    @mock.patch("core.services.business_logic.get_all_objects_from_order_items")
    def test_delete_order_and_order_items(
        self, mock_get_all_order_items, mock_delete_all_items, mock_delete_order
    ):
        """Testing the logic for deleting Order and OrderItems"""
        mock_get_all_order_items.return_value = "test_get_all_order_items"
        mock_delete_all_items.return_value = "test_delete_all_items"
        mock_delete_order.return_value = "test_delete_order"

        # Assert that fucntion return a correct response
        self.assertEqual(delete_order_and_order_items(user="test_user"), True)

        # Assert that fucntion get_all_objects_from_order_items has been called
        mock_get_all_order_items.assert_called_once()

        # Assert that fucntion delete_all_items_from_order has been called
        mock_delete_all_items.assert_called_once()

        # Assert that fucntion delete_order has been called
        mock_delete_order.assert_called_once()
