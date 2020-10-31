from django.dispatch import receiver, Signal

post_create_user = Signal()


@receiver(post_create_user)
def callback(sender, **kwargs):
    from ..models import PrivacySettings
    print('Created profile model.')
    PrivacySettings.objects.create(profile=sender)
    print('Created PrivacySettings model.')
