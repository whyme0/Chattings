from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import viewsets

from .permissions import IsOwnerOrAuthenticatedOrReadOnly
from .serializers import ChatSerializer
from apps.chats.models import Chat


class ChatViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAuthenticatedOrReadOnly]
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ChatMembersView(RetrieveAPIView):
    queryset = Chat.objects.all()

    def retrieve(self, request, *args, **kwargs):
        chat = self.get_object()
        return Response({'members': chat.members})
