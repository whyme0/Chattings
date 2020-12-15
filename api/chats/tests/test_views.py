from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from ..views import ChatViewSet
from apps.users.models import Profile
from apps.chats.models import Chat

class TestChatViewSet_List(APITestCase):
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


class TestChatViewSet_Retrieve(APITestCase):
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
