from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Chat


class ChatsList(ListView):
    model = Chat
    paginate_by = 16
    ordering = '?'
    context_object_name = 'chats'
    template_name = 'chats/chats_list/chats_list.html'


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
@method_decorator(never_cache, name='dispatch')
class ChatCreateView(CreateView):
    model = Chat
    template_name = 'chats/create_chat/create_chat.html'
    fields = ['label', 'description', 'name', 'avatar']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('chats:chat-list')


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class ChatView(DetailView):
    model = Chat

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return HttpResponse('This part of site is under development.')
