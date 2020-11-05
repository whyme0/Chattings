from typing import Dict, List

from rest_framework import serializers

from apps.users.models import Profile


META_FIELDS: Dict[str, List[str]] = {
    'PROFILE_SERIALIZER_FIELDS': ['url', 'id', 'avatar_image'],
}


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = META_FIELDS['PROFILE_SERIALIZER_FIELDS']
        extra_kwargs = {
            'url': {'view_name': 'users:profile', 'lookup_field': 'pk'}
        }
