from django.contrib.contenttypes.models import ContentType
from django.core.validators import ValidationError
from django.contrib.auth.models import Permission
from django.db import IntegrityError, transaction
from django.test import TestCase

from ..models import Profile


class TestProfileModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = Profile.objects.create(
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
        Checks that Token model creates
        when create user model, and check it properties
        """
        # ev - email verification
        self.assertTrue(hasattr(self.u, 'token'))
        
        ev = self.u.token
        token = ev.token

        self.assertEqual(len(token), 140)
        self.assertLess(ev.creation_date, ev.expiration_date)

        ev.refresh()
        self.assertNotEqual(ev.token, token)
    
    def test_user_login_permission(self):
        self.assertNotIn(self.can_login_perm, self.u.user_permissions.all())
        self.u.user_permissions.add(self.can_login_perm)
        self.assertIn(self.can_login_perm, self.u.user_permissions.all())
