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
            password='hardpwd123',
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
    
    def test_template1(self):
        response = self.client.get(
            reverse('chats:chat-list'),
        )

        # Check that user see chats in template
        soup = BeautifulSoup(response.content, 'html.parser')
        chats = soup.find_all('div', 'chat__wrapper')

        self.assertEqual(len(chats), 10)

        # Check for proper image
        src_attr = chats[0].find('img')['src']
        self.assertEqual(src_attr, '/media/chats_avatars/default_chat_avatar.png')
    
    def test_template2(self):
        response = self.client.get(reverse('chats:chat-list'))

        # Check, that not authenticated user doesn't see create link button
        soup = BeautifulSoup(response.content, 'html.parser')
        create_link = soup.find('a', {'id': 'createChatLink'})
        self.assertIsNone(create_link)

        # Check, that authenticated user can see this link
        self.client.force_login(self.u1)
        response = self.client.get(reverse('chats:chat-list'))

        soup = BeautifulSoup(response.content, 'html.parser')
        create_link = soup.find('a', {'id': 'createChatLink'})

        self.assertIsNotNone(create_link)
        self.assertEqual(create_link['href'], reverse('chats:chat-create'))
