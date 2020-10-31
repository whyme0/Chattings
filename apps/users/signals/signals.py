from django.dispatch import receiver, Signal

post_create_user = Signal()


@receiver(post_create_user)
def callback(sender, **kwargs):
    from ..models import PrivacySettings
    PrivacySettings.objects.create(profile=sender)
