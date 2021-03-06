from time import sleep

from django.contrib.contenttypes.models import ContentType
from django.core.validators import ValidationError
from django.contrib.auth.models import Permission
from django.db import IntegrityError, transaction
from django.test import TestCase

from ..models import Profile, PasswordRecovery, Token, PrivacySettings


class TestProfileModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = Profile.objects.create_user(
            username='user001',
            email='email@mail.com',
            password='hardpwd123'
        )
    
    def setUp(self):
        content_type = ContentType.objects.get_for_model(Profile)
        self.can_login_perm = Permission.objects.create(
            codename='can_login',
            name='Can login to site',
            content_type=content_type,
        )

    def test_user_permissions(self):
        u1 = Profile.objects.create_superuser(
            username='user333',
            password='hardpwd123',
            email='mail@gmail.com'
        )
        u2 = Profile.objects.create_user(
            username='user334',
            password='hardpwd123',
            email='mail1@gmail.com'
        )

        self.assertTrue(u1.is_superuser)
        self.assertTrue(u1.is_staff)

        self.assertFalse(u2.is_superuser)
        self.assertFalse(u2.is_staff)
    
    def test_model_validators(self):
        """
        Check proper user model fields validation for
        'username', 'email'
        """
        u1 = Profile(username='ti*#(@', email='sp@com', password='12345')

        with self.assertRaises(ValidationError):
            u1.full_clean()
        
        try:
            u1.full_clean()
        except ValidationError as e:
            self.assertEqual(e.message_dict['email'][0], 'Enter a valid email address.')
            self.assertIn('Enter valid username.', e.message_dict['username'][0])

    def test_intergrityerror1(self):
        with self.assertRaises(IntegrityError):
            Profile.objects.create(username='user001', email='mail@mail.com',
                password='12345')
    
    def test_intergrityerror2(self):
        with self.assertRaises(IntegrityError):
            Profile.objects.create(username='user002', email='email@mail.com',
                password='12345')
    
    def test_user_email_verification(self):
        """
        Checks that EmailVerification model creates
        when create user model, and check it properties
        """
        # ev - email verification
        self.assertTrue(hasattr(self.u, 'email_verification'))
        
        ev = self.u.email_verification
        token = ev.token

        self.assertEqual(len(token), 140)
        self.assertLess(ev.creation_date, ev.expiration_date)

        ev.refresh()
        self.assertNotEqual(ev.token, token)
    
    def test_user_privacy_settings(self):
        """
        Checks that PrivacySettins models creates when
        create user model, and check it logic
        """
        self.u.refresh_from_db()
        # ps - profile settings
        self.assertTrue(hasattr(self.u, 'privacy_settings'))
        ps = self.u.privacy_settings


    def test_user_login_permission(self):
        self.assertNotIn(self.can_login_perm, self.u.user_permissions.all())
        self.u.user_permissions.add(self.can_login_perm)
        self.assertIn(self.can_login_perm, self.u.user_permissions.all())    


        
class TestPasswordRecoveryModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = Profile.objects.create_user(
            username='username',
            email="email@m.c",
            password='hardpwd123',
        )
    
    def test_model_properties(self):
        """
        Check that model successfully creates
        """
        pwd_recovery = PasswordRecovery.objects.create(profile=self.u)


class TestTokenModel(TestCase):
    def test_model_properties(self):
        """
        Check that model successfully creates and
        check it properties
        """
        t = Token.objects.create()

        self.assertEqual(len(t.token), 140)
        self.assertLess(t.creation_date, t.expiration_date)

        old_token = t.token
        old_creation_date = t.creation_date
        old_expiration_date = t.expiration_date

        # Simulates waiting because sometimes test executes so quickly
        # that time between initializing old_expiration_date and
        # refreshing token model equals to zero, so old_creation_date == t.creation_date
        # but this should not equal.
        sleep(0.025)
        t.refresh()

        self.assertNotEqual(old_token, t.token)
        self.assertNotEqual(old_creation_date, t.creation_date)
        self.assertNotEqual(old_expiration_date, t.expiration_date)


class TestPrivacySettingsModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = Profile.objects.create_user(
            username='user001',
            email='email@mail.com',
            password='hardpwd123'
        )
    
    def setUp(self):
        content_type = ContentType.objects.get_for_model(Profile)
        self.can_login_perm = Permission.objects.create(
            codename='can_login',
            name='Can login to site',
            content_type=content_type,
        )
    
    def test_proper_model_behavior(self):
        # ps - privacy settings
        ps = self.u.privacy_settings
        
        self.assertEqual(len(PrivacySettings.objects.all()), 1)

        self.u.delete()

        self.assertEqual(len(PrivacySettings.objects.all()), 0)
        with self.assertRaises(PrivacySettings.DoesNotExist):
            PrivacySettings.objects.get(profile=self.u)
