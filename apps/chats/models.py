from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxLengthValidator
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

    members = ArrayField(
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

    def add_member_by_id(self, user_id):
        """Use this method instead of direct item adding"""
        if user_id not in self.members:
            self.members.append(user_id)

    def get_name(self):
        return '@'+self.name

    def __str__(self):
        return self.name
