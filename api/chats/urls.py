from django.urls import path

from .views import ChatViewSet, ChatMembersView

chats_list = ChatViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
chat_details = ChatViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    path(
        'chats/',
        chats_list,
        name='api-chat-list',
    ),

    path(
        'chats/<int:pk>',
        chat_details,
        name='api-chat-details',
    ),

    path(
        'chats/<int:pk>/members',
        ChatMembersView.as_view(),
        name='api-chat-members',
    ),
]