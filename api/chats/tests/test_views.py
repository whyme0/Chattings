from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from ..views import ChatViewSet
from apps.users.models import Profile
from apps.chats.models import Chat

class TestChatViewSet__List(APITestCase):
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
            reverse('api-chat-list'),
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)


class TestChatViewSet__Create(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u1 = Profile.objects.create_user(
            username='testuser',
            email='testuser@mail.com',
            password='hardpwd123',
        )
    
    def test_for_create(self):
        self.assertEqual(Chat.objects.filter(name='name1').count(), 0)
        self.client.force_login(self.u1)
        response = self.client.post(
            reverse('api-chat-list'),
            data={
                'label': 'Chat1',
                'name': 'name1',
            },
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Chat.objects.filter(name='name1').count(), 1)
        self.assertEqual(Chat.objects.get(name='name1').owner, self.u1)
    
    def test_for_errors(self):
        self.client.force_login(self.u1)
        response = self.client.post(
            reverse('api-chat-list'),
            format='json',
            follow=True,
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['label'][0], 'This field is required.')
        self.assertEqual(response.data['name'][0], 'This field is required.')


class TestChatViewSet__Retrieve(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u1 = Profile.objects.create_user(
            username='testuser',
            email='testuser@mail.com',
            password='hardpwd123',
        )

        cls.chat1 = Chat.objects.create(
            owner=cls.u1,
            label='Label №1',
            name='name_1',
        )
    
    def test_basics(self):
        self.client.force_login(self.u1)
        response = self.client.get(
            reverse('api-chat-details', kwargs={'pk': self.chat1.pk}),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.chat1.id)
        self.assertEqual(response.data['label'], self.chat1.label)
        self.assertEqual(response.data['name'], self.chat1.name)
        self.assertIn(
            reverse('chats:chat', kwargs={'pk': self.chat1.pk}),
            response.data['url'])
        self.assertIn(
            reverse('api-profile', kwargs={'pk': self.u1.pk}),
            response.data['owner'])


class TestChatMembersView(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u1 = Profile.objects.create_user(
            username='testuser',
            email='testuser@mail.com',
            password='hardpwd123',
        )

        cls.chat1 = Chat.objects.create(
            owner=cls.u1,
            label='Label №1',
            name='name_1',
        )

        for i in range(1, 5):
            Profile.objects.create_user(
                username=f'testuser{i}',
                email=f'testuser{i}@mail.co',
                password='hardpwd123',
            )

    def setUp(self):
        for profile in Profile.objects.all():
            self.chat1.add_member_by_id(profile.id)
            self.chat1.save()
    
    def test_basics(self):
        response = self.client.get(
            reverse('api-chat-members', kwargs={'pk': self.chat1.pk}),
            format='json',
        )

        self.assertEqual(len(response.data['members']), 5)


class TestChatViewSet__Partial_Update(APITestCase):
    pass


class TestChatViewSet__Destroy(APITestCase):
    pass

