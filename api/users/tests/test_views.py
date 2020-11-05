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
    
    def test_basics(self):
        response = self.client.get(
            reverse('api-profile', kwargs={'pk': self.u1.pk}),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_for_profile(self):
        expecting_profile_data = {
            'id': self.u2.id,
            'url': 'http://testserver' + reverse('users:profile', kwargs={'pk': self.u2.pk}),
        }
        response = self.client.get(
            reverse('api-profile', kwargs={'pk': self.u2.pk}),
            format='json',
        )

        for k, v in expecting_profile_data.items():
            self.assertEqual(v, response.data[k])
    
    def test_for_404_resposne(self):
        response = self.client.get(
            reverse('api-profile', kwargs={'pk': 89234}),
            format='json',
        )


        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(str(response.data['detail']), 'Not found.')
