from typing import Dict, List

from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from apps.chats.models import Chat


META_FIELDS: Dict[str, List[str]] = {
    'CHAT_SERIALIZER_FIELDS': [
        'url', 'id', 'owner', 'label',
        'description', 'name', 'avatar'],
}


class ChatSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.SlugField(
        max_length=50,
        help_text='Name must be unique and cannot be changed.',
    )

    def validate_name(self, value):
        if self.instance and self.instance.name != value:
            raise ValidationError('You can\'t edit this field')
        return value

    class Meta:
        model = Chat
        fields = META_FIELDS['CHAT_SERIALIZER_FIELDS']
        extra_kwargs = {
            'url': {'view_name': 'chats:chat', 'lookup_field': 'pk'},
            'owner': {'view_name': 'api-profile', 'lookup_field': 'pk'},
        }
