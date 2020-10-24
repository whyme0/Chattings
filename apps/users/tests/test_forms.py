from django.test import TestCase

from ..forms import AskEmailForm, PasswordResetForm
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


class TestPasswordResetForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = Profile.objects.create_user(
            username='temp1',
            email='temp1@mail.co',
            password='hardpwd123',
        )
    
    def test_form_validation_for_errors(self):
        f1 = PasswordResetForm(
            user=self.u,
            data={
                'new_password1': '123',
                'new_password2': '123',
            }
        )

        errs = list(f1.errors.values())[0]

        self.assertFalse(f1.is_valid())

        self.assertIn('This password is too short. It must contain at least 8 characters.', errs)
        self.assertIn('This password is too common.', errs)
        self.assertIn('This password is entirely numeric.', errs)

        f2 = PasswordResetForm(
            user=self.u,
            data={
                'new_password1': 'uiuiuiui',
                'new_password2': 'iuiuiuiu',
            }
        )

        errs = list(f2.errors.values())[0]
        self.assertFalse(f2.is_valid())

        self.assertIn('The two password fields didn’t match.', errs)

    def test_form_validation_for_success(self):
        self.assertTrue(self.u.check_password('hardpwd123'))

        f1 = PasswordResetForm(
            user=self.u,
            data={
                'new_password1': 'goodPwd345',
                'new_password2': 'goodPwd345',
            }
        )

        self.assertTrue(f1.is_valid())
        f1.save()

        self.assertFalse(self.u.check_password('hardpwd123'))
        self.assertTrue(self.u.check_password('goodPwd345'))
