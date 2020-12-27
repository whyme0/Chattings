from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpRequest
from django.views.generic import (FormView, TemplateView, RedirectView,
    DetailView, View)
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.messages import error, success
from django.contrib.auth.models import Permission
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.db.models import Q


from .utils import (perform_email_verification, confirm_email,
    find_user_or_404, find_user, perform_password_recovery, recover_password)
from .forms import (UserLoginForm, UserRegistrationForm, AskEmailForm,
    PasswordResetForm, PrivacySettingsForm, UserPasswordChangeForm,
    ProfileAvatarForm)
from .models import Profile, PasswordRecovery


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
    
    def get_success_url(self):
        return reverse('users:profile', kwargs={'pk': self.request.user.pk})
    
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
    redirect_authenticated_user = True

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = settings.REGISTRATION_REDIRECT_URL
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your REGISTRATION_REDIRECT_URL doesn't point to a login page."
                )
            return redirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

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

        return redirect('users:perform_password_recovery')


class PasswordResetView(FormView):
    form_class = PasswordResetForm
    template_name = 'users/password_reset.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.get_from_token(self.kwargs['token']).profile
        return kwargs

    def get_from_token(self, token):
        """Return PasswordRecovery model by token"""
        self.pwd_recovery = None
        try:
            self.pwd_recovery = PasswordRecovery.objects.get(token=token)
            if self.pwd_recovery.is_token_expired():
                raise SuspiciousOperation('Token expired.')
        except PasswordRecovery.DoesNotExist:
            raise SuspiciousOperation('Token doesn\'t exist.')
        if self.pwd_recovery:
            return self.pwd_recovery

    def form_valid(self, form):
        recover_password(form, self.pwd_recovery, self.request)
        return redirect('users:login')


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class ProfileLogoutView(RedirectView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.get_redirect_url())
    
    def get_redirect_url(self, *args, **kwargs):
        super().get_redirect_url(*args, **kwargs)
        return reverse('users:login')


class ProfileView(DetailView):
    """
    View with detailed information for specific profile model
    """
    template_name = 'users/profiles/profile_details.html'
    context_object_name = 'profile'
    model = Profile

    def get_context_data(self, *args, **kwargs):
        profile = self.get_object()
        ctx = super().get_context_data(*args, **kwargs)
        ctx['profile_info'] = profile.privacy_settings.get_public_info().items()
        ctx['profile_chats'] = profile.get_active_chats()
        return ctx


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
@method_decorator(never_cache, name='dispatch')
class ProfileEditView(TemplateView):
    template_name = 'users/profiles/edit_profile.html'
    change_password_form = UserPasswordChangeForm
    privacy_settings_form = PrivacySettingsForm
    profile_avatar_form = ProfileAvatarForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['privacy_settings_form'] = self.privacy_settings_form(self.request.user)
        ctx['password_change_form'] = self.get_password_change_form_for_ctx()
        ctx['profile_avatar_form'] = self.get_profile_avatar_form_for_ctx()
        return ctx

    def post(self, request, *args, **kwargs):
        if request.GET.get('form_type') == 'change_password_form':
            response = self.proceed_change_password_form(request)
            return response
        elif request.GET.get('form_type') == 'change_profile_avatar_form':
            response = self.proceed_avatar_change_form(request)
            return response
        return HttpResponseBadRequest('Server cannot proceed this request')

    def proceed_change_password_form(self, r: HttpRequest) -> HttpResponse:
        form = self.change_password_form(r.user, r.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('users:login'))

        return render(r, self.template_name, self.get_context_data())
    
    def proceed_avatar_change_form(self, r: HttpRequest) -> HttpResponse:
        form = self.profile_avatar_form(r.POST, r.FILES, instance=r.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('users:edit-profile'))
        
        return render(r, self.template_name, self.get_context_data())
    
    def get_password_change_form_for_ctx(self):
        if self.request.method == 'POST':
            return self.change_password_form(
                self.request.user,
                self.request.POST)
        return self.change_password_form(self.request.user)
    
    def get_profile_avatar_form_for_ctx(self):
        if self.request.method == 'POST':
            return self.profile_avatar_form(
                self.request.POST,
                instance=self.request.user)
        return self.profile_avatar_form(instance=self.request.user)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class PrivacySettingsFormHandlerView(View):
    http_method_names = ['post']
    def post(self, request, *args, **kwargs):
        form = PrivacySettingsForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Form successfully saved.')
        raise SuspiciousOperation('Invalid post data.')
