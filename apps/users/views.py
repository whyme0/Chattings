from django.views.generic import (FormView, TemplateView, RedirectView,
    DetailView)
from django.contrib.auth import login, authenticate
from django.contrib.messages import error, success
from django.contrib.auth.models import Permission
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.http import Http404
from django.db.models import Q


from .utils import (perform_email_verification, confirm_email,
    find_user_or_404, find_user, perform_password_recovery)
from .forms import UserLoginForm, UserRegistrationForm, AskEmailForm
from .models import Profile, EmailVerification


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    form_class = UserLoginForm

    def form_valid(self, *args, **kwargs):
        user = find_user(self.request.POST.get('username'))
        # If user don't confirm his email address
        if not user.has_perm('users.can_login'):
            error(self.request, 'Confirm your email to login.',
                'email-not-confirmed')
            return redirect(reverse('users:login')
                + f'?username={user.username}')

        return super().form_valid(*args, **kwargs)
    
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        link = reverse('users:resend_confirmation_email')\
             + (f'?redirect_to={reverse("users:login")}'
             f'&username={self.request.GET.get("username")}')
        ctx.update({'resend_email': link})
        return ctx


class UserRegistrationView(FormView):
    template_name = 'users/registration.html'
    success_url = '/auth/login/'
    form_class = UserRegistrationForm

    def form_valid(self, form_class=None):
        user = Profile.objects.create_user(
            username=self.request.POST['username'],
            email=self.request.POST['email'],
            password=self.request.POST['password1'])
        
        perform_email_verification(user, self.request)
        
        return super().form_valid(form_class)


class EmailConfirmationView(TemplateView):
    """
    View that confirm email address for specific user
    with token from slug in url.
    """
    template_name = 'users/emailconfirmation.html'

    def get(self, request, *args, **kwargs):
        confirm_email(kwargs['token'], request)
        return super().get(request, *args, **kwargs)


class ResendEmailConfirmation(RedirectView):
    """
    View that resend email confirmation letter.
    This can be useful when user forgot to confirm in
    time email i.e. token was expired
    """
    def dispatch(self, request, *args, **kwargs):
        # This view demand redirect_to and username url parameters
        if not ((request.GET.get('redirect_to'))\
           and (request.GET.get('username'))):
            raise Http404('Page does not exist.')
        
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = find_user_or_404(request.GET.get('username'))
        
        # If email not confirmed
        if hasattr(user, 'email_verification'):
            perform_email_verification(user, request, update_verification=True)
        else:
            raise Http404('Page does not exist.')
        
        return redirect(self.get_redirect_url(*args, **kwargs))
    
    def get_redirect_url(self, *args, **kwargs):
        return self.request.GET.get('redirect_to')


class AskEmailForPasswordRecoveryView(FormView):
    """
    This view with form in template ask user for email
    on which will be sent password recovery link.
    """
    form_class = AskEmailForm
    template_name = 'users/ask_email_for_pwd_recovery.html'

    def form_valid(self, form):
        perform_password_recovery(form.cleaned_data['email'], self.request)


class ProfileView(DetailView):
    pass
