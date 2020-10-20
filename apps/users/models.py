from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.utils import timezone
from django.db import models

from .validators import UsernameRegexValidator 
from .utils import generate_token


def user_directory_upload(instance, filename):
    return 'user_avatars/{0}'.format(instance.username)


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


class Profile(AbstractUser):
    avatar_image = models.ImageField(
        upload_to=user_directory_upload,
        blank=True,
        default='user_avatars/default_user_avatar.png',
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
