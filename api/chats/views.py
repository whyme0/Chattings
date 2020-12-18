from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import viewsets

from .serializers import ChatSerializer
from apps.chats.models import Chat


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer


class ChatMembersView(RetrieveAPIView):
    queryset = Chat.objects.all()

    def retrieve(self, request, *args, **kwargs):
        chat = self.get_object()
        return Response({'members': chat.members})
