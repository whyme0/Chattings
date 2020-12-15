from typing import Dict, List

from rest_framework import serializers

from apps.chats.models import Chat


META_FIELDS: Dict[str, List[str]] = {
    'CHAT_SERIALIZER_FIELDS': [
        'url', 'id', 'owner', 'label',
        'description', 'name', 'avatar'],
}


class ChatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Chat
        fields = META_FIELDS['CHAT_SERIALIZER_FIELDS']
        extra_kwargs = {
            'url': {'view_name': 'chats:chat', 'lookup_field': 'pk'},
            'owner': {'view_name': 'api-profile', 'lookup_field': 'pk'},
        }
