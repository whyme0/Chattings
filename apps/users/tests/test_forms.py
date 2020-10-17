from django.test import TestCase

from ..forms import AskEmailForm
from ..models import Profile


class TestAskEmailForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = Profile.objects.create_user(
            username='tempuser',
            email='tempmail@mail.co',
            password='hardpwd123',
        )
    
    def test_form_validation_for_errors(self):
        """
        Test that form validators works fine
        """
        f = AskEmailForm(data={'email': 'wrong@mail'})

        errors = list(f.errors.values())[0]
        self.assertFalse(f.is_valid())
        self.assertIn('Enter a valid email address.', errors)
        self.assertIn('User with this email doesn\'t exist.', errors)
    
    def test_form_validation_for_success(self):
        """
        Test that form can determine valid data
        """
        f = AskEmailForm(data={'email': 'tempmail@mail.co'})
        self.assertTrue(f.is_valid())
