from django.test import TestCase
from django.urls import reverse
from bs4 import BeautifulSoup

from ..views import ChatsList, ChatView, ChatCreateView
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
            Chat.objects.create(
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


class TestChatView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u1 = Profile.objects.create_user(
            username='testuser',
            email='testuser@mail.com',
            password='hardpwd123',
        )

        cls.c1 = Chat.objects.create(
            owner=cls.u1,
            label='Chat 1',
            name='chat1',
            members=[cls.u1.id],
        )

    def test_basics(self):
        response = self.client.get(
            reverse('chats:chat', kwargs={'pk': self.u1.pk}),
            follow=True,
        )

        self.assertEqual(response.resolver_match.view_name, 'users:login')

        self.client.force_login(self.u1)
        response = self.client.get(
            reverse('chats:chat', kwargs={'pk': self.c1.pk})
        )

        title = BeautifulSoup(response.content, 'html.parser').find('title').getText().strip().replace('\n', '')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, ChatView)
        self.assertEqual(title, self.c1.label + ' \\ Chattings')
    
    def test_template(self):
        self.client.force_login(self.u1)
        response = self.client.get(
            reverse('chats:chat', kwargs={'pk': self.c1.pk}),
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        description = soup.find('div', 'chat__modal__description')
        chat_label = soup.find('div', 'chat__label')
        members = soup.find('div', 'chat__modal__members')

        self.assertEqual(description.get_text().replace('\n', ''), 'Description: ---')
        self.assertEqual(members.get_text().replace('\n', ''), 'Members: 1')
        self.assertEqual(chat_label.get_text().replace('\n', ''), self.c1.label)


class TestChatCreateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u1 = Profile.objects.create_user(
            username='testuser',
            email='testuser@mail.com',
            password='hardpwd123',
        )
    
    def test_basics(self):
        response = self.client.get(
            reverse('chats:chat-create'),
            follow=True,
        )

        self.assertEqual(response.resolver_match.view_name, 'users:login')

        self.client.force_login(self.u1)
        response = self.client.get(
            reverse('chats:chat-create')
        )

        title = BeautifulSoup(response.content, 'html.parser').find('title').getText().strip().replace('\n', '')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, ChatCreateView)
        self.assertEqual(title, 'Create new chat \\ Chattings')
    
    def test_create_model(self):
        name = 'chat-name'
        with self.assertRaises(Chat.DoesNotExist):
            Chat.objects.get(name=name)
        
        self.client.force_login(self.u1)
        response = self.client.post(
            reverse('chats:chat-create'),
            data={
                'label': 'Chat X',
                'name': name,
            },
            follow=True,
        )

        self.assertEqual(response.resolver_match.func.view_class, ChatView)
        chats = Chat.objects.filter(name=name)
        self.assertEqual(len(chats), 1)
    
    def test_for_errors(self):
        self.client.force_login(self.u1)
        response = self.client.post(
            reverse('chats:chat-create'),
            data={
                'label': '',
                'name': 'wrong format',
            },
            follow=True,
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        errors = soup.findAll('p', 'field_error')

        self.assertEqual(errors[0].get_text(), 'This field is required.')
        self.assertEqual(errors[1].get_text(), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.')


class TestDeleteChatView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u1 = Profile.objects.create_user(
            username='testuser1',
            email='testmail1@mail.co',
            password='hardpwd123',
        )
        cls.u2 = Profile.objects.create_user(
            username='testuser2',
            email='testmail2@mail.co',
            password='hardpwd123',
        )

        cls.c1 = Chat.objects.create(
            label='Chat1',
            name='chat1',
            owner=cls.u1,
        )

    def test_for_404(self):
        self.client.force_login(self.u1)
        response = self.client.get(
            reverse('chats:chat-delete', kwargs={'pk': '1000'}),
            follow=True,
        )

        self.assertEqual(response.status_code, 404)
    
    def test_for_400(self):
        self.client.force_login(self.u2)
        response = self.client.get(
            reverse('chats:chat-delete', kwargs={'pk': self.c1.pk}),
            follow=True,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode('utf-8'), 'No way.')
    
    def test_for_delete(self):
        self.assertEqual(Chat.objects.all().count(), 1)

        self.client.force_login(self.u1)
        response = self.client.get(
            reverse('chats:chat-delete', kwargs={'pk': self.c1.pk}),
            follow=True,
        )

        self.assertEqual(Chat.objects.all().count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.view_class, ChatCreateView)
