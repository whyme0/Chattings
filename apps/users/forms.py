from typing import Dict

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (AuthenticationForm, SetPasswordForm,
    UserCreationForm, UsernameField, PasswordChangeForm)
from django.core.exceptions import ValidationError

from .models import PrivacySettings, Profile
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


class PasswordResetForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.fields['new_password1'].widget.attrs['class'] = 'field'
        self.fields['new_password1'].help_text = ''
        self.fields['new_password2'].widget.attrs['class'] = 'field'
        self.fields['new_password2'].help_text = ''


class AskEmailForm(forms.Form):
    email = forms.EmailField(
        validators=[username_exist_validator],
        help_text='We will sent password recovery letter on this email',
        widget=forms.EmailInput(attrs={'class': 'field'})
    )


class PrivacySettingsForm(forms.ModelForm):
    class Meta:
        model = PrivacySettings
        exclude = ['profile']
    
    def __init__(self, profile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.instance = profile.privacy_settings
        
        self._set_default_values(profile.privacy_settings)

    def _set_default_values(self, privacy_settings: PrivacySettings):
        """
        Set default values to form fields based on data
        from related PrivacySettings model
        """
        data = self._normalize_data(privacy_settings.get_public_info())

        for k, v in data.items():
            if v:
                self.fields[k].widget.attrs['checked'] = ''

    def _normalize_data(self, data: dict) -> Dict[str, bool]:
        """
        Convert data from passed data to proper format

        Example: 'Some field' to 'is_some_field_public'
        """
        normalized_data = {}
        for k, v in data.items():
            field_name = k.lower().replace(' ', '_')
            field_name = 'is_{}_public'.format(field_name)
            field_value = v != 'Hidden'
            normalized_data[field_name] = field_value
        return normalized_data


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['new_password1'].widget.attrs['class'] = 'field'
        self.fields['new_password1'].help_text = ''
        self.fields['new_password2'].widget.attrs['class'] = 'field'
        self.fields['new_password2'].help_text = ''
        self.fields['old_password'].widget.attrs['class'] = 'field'
        self.fields['old_password'].help_text = ''


class ProfileAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar_image']
