from django.contrib.auth.models import UserManager

from .signals.signals import post_create_user


class ProfileManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        We override this method because we need to do some
        additional step after creating user
        """
        user = super()._create_user(username, email, password, **extra_fields)
        post_create_user.send(sender=user)
        return user
