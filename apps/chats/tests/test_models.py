from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.db.utils import DataError
from django.test import TestCase

from ..models import Chat
from apps.users.models import Profile


class TestChatModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u = Profile.objects.create_user(
            username='testuser',
            email='testuser@mail.com',
            password='hardpwd123'
        )
    
    def test_success_creation(self):
        chat_name = 'test_chat'
        chat = Chat.objects.create(
            owner=self.u,
            label='Test Chat',
            name=chat_name,
        )

        self.assertEqual(chat.name, '@'+chat_name)
    
    def test_model_validators(self):
        with self.assertRaises(DataError):
            chat = Chat.objects.create(
                owner=self.u,
                label='Test Chat',
                name='a'*51,
            )
