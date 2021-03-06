from datetime import timedelta

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import EmailValidator
from django.utils import timezone
from django.db import models

from .validators import UsernameRegexValidator, image_size_validator
from .managers import ProfileManager
from .utils import generate_token


def user_directory_upload(instance, filename):
    return 'users_avatars/{0}/{1}'.format(instance.username, filename)


class Profile(AbstractUser):
    avatar_image = models.ImageField(
        upload_to=user_directory_upload,
        blank=True,
        default='users_avatars/default_user_avatar.png',
        help_text='Max image size 1mb.',
        validators=[image_size_validator]
    )

    username = models.CharField(
        help_text='Required. 45 characters or fewer. Letters, digits and -/_ only.',
        max_length=45,
        validators=[UsernameRegexValidator()],
        error_messages={
            'unique': ('A user with that username already exists.'),
        },
        unique=True,
    )

    email = models.EmailField(
        blank=False,
        unique=True,
    )

    objects = ProfileManager()

    def save(self, **kwargs):
        super().save(**kwargs)

        # When profile creates in first time
        if not EmailVerification.objects.filter(profile=self):
            EmailVerification(profile=self).save()

    def __str__(self):
        return self.email
    
    def is_email_confirmed(self):
        try:
            self.email_verification
            return False
        except EmailVerification.DoesNotExist:
            return True
    
    def get_active_chats(self):
        """Return queryset of chats with specific Profile"""
        from ..chats.models import Chat
        return Chat.objects.filter(members__contains=[self.id])


class Token(models.Model):
    """
    Model with data to help recover passowrd, registrate user, etc.
    by email using unique token.

     Attrs:
       token - token which determine
       creation_date - date when model was created
       expiration_date - date when the token will cease to be valid
    """

    token = models.SlugField(
        unique=True,
        max_length=140,
        blank=True,
    )

    creation_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    
    def save(self, **kwargs):
        self.token = generate_token(140)
        self.creation_date = timezone.now()
        self.expiration_date = timezone.now() + timedelta(hours=1)
        return super().save(**kwargs)

    def refresh(self):
        """
        Refresh data in model such as token, creation_date, expiration_date
        """
        self.save()

    def __str__(self):
        return f'Created at: {self.creation_date}'
    
    def is_token_expired(self):
        return timezone.now() > self.expiration_date


class EmailVerification(Token):
    """
    Model with data to help confirm user by email

     Attrs:
       profile - profile which need to be confirmed.
    """
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='email_verification',
    )

    def __str__(self):
        return f'{self.profile.email}: {self.creation_date}'


class PasswordRecovery(Token):
    """
    Model with data to help recover password by email.

     Attrs:
       profile - profile which need to recover password
    """
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='password_recovery',
    )

    def __str__(self):
        return f'{self.profile.email}: {self.creation_date}'


class PrivacySettings(models.Model):
    """
    PrivacySettings need to let profile determine which
    model data will be public and can be viewed by other users.
    """
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='privacy_settings'
    )

    is_username_public = models.BooleanField(default=False)
    is_email_public = models.BooleanField(default=False)
    is_date_joined_public = models.BooleanField(default=False)

    def get_public_info(self) -> dict:
        # Problem of this function is that when one day another programmer will
        # change (e.g. add/remove) current model's fields then programmer
        # also will need to correcy this function. Such way is very dirty.
        p = self.profile
        return {
            'Username': p.username if self.is_username_public else 'Hidden',
            'Email': p.email if self.is_email_public else 'Hidden',
            'Date joined': p.date_joined if self.is_date_joined_public else 'Hidden',
        }

    def __str__(self):
        return str(self.profile.username)
