from django.urls import path

from . import views

app_name = 'chats'
urlpatterns = [
    path(
        'list/',
        views.ChatsList.as_view(),
        name='chat-list',
    ),

    path(
        'create/',
        views.ChatCreateView.as_view(),
        name='chat-create',
    ),

    path(
        '<int:pk>',
        views.ChatView.as_view(),
        name='chat',
    ),

    path(
        '<int:pk>/delete',
        views.DeleteChatView.as_view(),
        name='chat-delete',
    ),
]