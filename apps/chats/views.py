from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, DetailView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic.base import RedirectView
from django.shortcuts import render, redirect
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
    fields = ['label', 'description', 'name', 'avatar']
    template_name = 'chats/create_chat/create_chat.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('chats:chat', kwargs={'pk': self.object.pk})


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class ChatView(DetailView):
    model = Chat
    context_object_name = 'chat'
    template_name = 'chats/chat_details/chat_details.html'


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class DeleteChatView(RedirectView, SingleObjectMixin):
    queryset = Chat.objects.all()
    http_method_names = ['get']
    template_name = 'chats/chat_delete/chat_delete.html'

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        chat = self.get_object()

        if request.user == chat.owner:
            chat.delete()
            return redirect(self.get_redirect_url())
        else:
            return HttpResponseBadRequest('No way.')

    def get_redirect_url(self, *args, **kwargs):
        return reverse('chats:chat-create')


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class EditChatView(UpdateView):
    model = Chat
    context_object_name = 'chat'
    fields = ['label', 'description', 'avatar']
    template_name = 'chats/chat_edit/chat_edit.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().owner:
            return HttpResponseBadRequest('No way.')
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('chats:chat-edit', kwargs={'pk':self.get_object().pk})
