from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.db.utils import DataError
from django.test import TestCase

from ..models import Chat
from apps.users.models import Profile


class TestChatModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u1 = Profile.objects.create_user(
            username='testuser',
            email='testuser@mail.com',
            password='hardpwd123'
        )
        cls.u2 = Profile.objects.create_user(
            username='testuser2',
            email='testuser2@mail.co',
            password='hardpwd123',
        )

        cls.chat = Chat.objects.create(
            owner=cls.u1,
            label='Test Chat',
            name='test_chat',
        )
    
    def test_success_creation(self):
        self.assertEqual(self.chat.name, '@test_chat')
    
    def test_model_validators(self):
        with self.assertRaises(DataError):
            self.chat = Chat.objects.create(
                owner=self.u1,
                label='Test Chat',
                name='a'*51,
            )

    def test_add_member_method(self):
        """
        'add_member' is a method of self.chat model instance
        """
        self.chat.add_member_by_id(self.u1.id)
        self.chat.add_member_by_id(self.u2.id)
        # Trying to add above members twice
        self.chat.add_member_by_id(self.u1.id)
        self.chat.add_member_by_id(self.u2.id)

        self.assertEqual(len(self.chat.members), 2)
