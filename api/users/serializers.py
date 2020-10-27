from rest_framework import serializers

from apps.users.models import Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ['url', 'id', 'username', 'avatar_image', 'date_joined']
        extra_kwargs = {
            'url': {'view_name': 'users:profile', 'lookup_field': 'pk'}
        }
