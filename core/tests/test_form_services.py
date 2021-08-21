from core.services.form_services import validate_from_for_whitespaces
from django.test import TestCase

class TestValidatorForm(TestCase):

    def test_validator_form(self):
        """Testing validator forms"""
        
        #Situation when form contains white spaces
        self.assertTrue(validate_from_for_whitespaces(['test','test','test']))

        #Situation when form doesn't contains white spaces
        self.assertFalse(validate_from_for_whitespaces(['', 'test', 'test']))