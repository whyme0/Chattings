from rest_framework import serializers

from apps.users.models import Profile


class UserSerializer(serializers.Sea):
    class Meta:
        model = Profile
        fields = ['id', 'username', 'avatar_image', 'date_joined']
