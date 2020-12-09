from django.views.generic import ListView
from django.shortcuts import render

from .models import Chat


class ChatsList(ListView):
    model = Chat
    paginate_by = 16
    ordering = '?'
    context_object_name = 'chats'
    template_name = 'chats/chats_list/template.html'
