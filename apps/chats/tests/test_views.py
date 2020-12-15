from django.test import TestCase
from django.urls import reverse
from bs4 import BeautifulSoup

from ..views import ChatsList
from ..models import Chat
from apps.users.models import Profile


class TestChatsListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u1 = Profile.objects.create_user(
            username='testuser',
            email='testuser@mail.com',
            password='hardpwd123'
        )

        for i in range(1, 11):
            chat1 = Chat.objects.create(
                owner=cls.u1,
                label=f'Label №{i}',
                name=f'name_{i}',
            )

    def test_basics(self):
        response = self.client.get(
            reverse('chats:chat-list'),
        )

        page_title = BeautifulSoup(response.content, 'html.parser').find('title').getText().strip().replace('\n', '')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(page_title, 'Chats list \ Chattings')
        self.assertEqual(response.resolver_match.func.view_class, ChatsList)
