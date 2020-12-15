from django.urls import path

from .views import ChatViewSet

chats_list = ChatViewSet.as_view({'get':'list'})
chat_details = ChatViewSet.as_view({'get':'retrieve'})

urlpatterns = [
    path('chats/', chats_list, name='api-chat-list'),
    path('chats/<int:pk>', chat_details, name='api-chat-details')
]