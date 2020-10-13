from rest_framework import serializers

from apps.users.models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'username', 'avatar_image', 'date_joined']
