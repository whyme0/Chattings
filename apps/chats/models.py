from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxLengthValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models


from .validators import validate_empty_string
from ..users.models import Profile


def chat_avatars_directory(instance, filename):
    return 'chats_avatars/{0}'.format(instance.name)


class Chat(models.Model):
    owner = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='chats'
    )
    
    # List of users id
    moderators = ArrayField(
        base_field=models.PositiveBigIntegerField(),
        default=list,
        blank=True,
        null=True,
    )
    
    label = models.CharField(
        max_length=70,
        validators=[validate_empty_string],
    )

    description = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    name = models.SlugField(
        max_length=51,
        validators=[MaxLengthValidator(50)],
        unique=True,
    )

    avatar = models.ImageField(
        upload_to=chat_avatars_directory,
        blank=True,
        default='chats_avatars/default_chat_avatar.png',
    )

    def __str__(self):
        return self.name


@receiver(pre_save, sender=Chat)
def pre_save_chat(sender, instance, **kwargs):
    if '@' not in instance.name:
        instance.name = '@' + instance.name
