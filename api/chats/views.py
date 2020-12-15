from rest_framework import viewsets

from .serializers import ChatSerializer
from apps.chats.models import Chat


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
