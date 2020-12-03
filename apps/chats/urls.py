from django.urls import path

from . import views

app_name = 'chats'
urlpatterns = [
    path(
        'list/',
        views.ChatsList.as_view(),
        name='chat-list',
    ),
]