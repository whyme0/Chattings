from django.contrib.auth.models import Permission, ContentType
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from apps.users.models import Profile
from .. import views


class TestProfileViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u1 = Profile.objects.create_user(
            username='temp1',
            email='temp1@mail.co',
            password='hardpwd123'
        )
        cls.u2 = Profile.objects.create_user(
            username='temp2',
            email='temp2@mail.co',
            password='hardpwd123',
        )

    def setUp(self):
        content_type = ContentType.objects.get_for_model(Profile)
        self.can_login_perm = Permission.objects.create(
            codename='can_login',
            name='Can login to site',
            content_type=content_type,
        )
    
    def test_basic(self):
        response1 = self.client.get(
            reverse('api-profiles'),
        )
        response2 = self.client.get(
            reverse('api-profile', kwargs={'pk': self.u1.pk}),
        )

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
    
    def test_for_profiles(self):
        response = self.client.get(
            reverse('api-profiles'),
            format='json'
        )
        u1_url = response.json()[0]['url']
        u2_url = response.json()[1]['url']
        
        r1 = self.client.get(u1_url)
        r2 = self.client.get(u2_url)
        
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[0]['username'], self.u1.username)
        self.assertEqual(response.json()[1]['username'], self.u2.username)


        self.assertEqual(r1.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
