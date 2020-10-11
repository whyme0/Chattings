from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
    UsernameField)
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django import forms

from .validators import username_exist_validator


class UserLoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].label = 'Username or email'
        self.fields['username'].validators += [username_exist_validator]
        self.fields['username'].widget.attrs['class'] = 'field'

        self.fields['password'].widget.attrs['class'] = 'field'

        self.error_messages['invalid_login'] = 'Enter correct password.'


class UserRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'field'

        self.fields['email'].widget.attrs['class'] = 'field'
        self.fields['email'].help_text = 'You will need to confirm email'

        self.fields['password1'].widget.attrs['class'] = 'field'
        self.fields['password1'].help_text = ''

        self.fields['password2'].widget.attrs['class'] = 'field'

    class Meta:
        model = get_user_model()
        fields = ('username', 'email')
        field_classes = {'username': UsernameField}
