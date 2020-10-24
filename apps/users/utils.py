from typing import Optional
from random import randint

from django.template.loader import render_to_string
from django.contrib.messages import success, error
from django.contrib.auth.models import Permission
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.http import Http404
from django.db.models import Q


CHARS = '1234567890qwertyuiopasdfghjklzxcvbnm'


def _random_upper(char: str) -> str:
    return char.upper() if randint(0, 1) else char


def generate_token(length: int) -> str:
    output = ''
    for i in range(length):
        output += _random_upper(CHARS[randint(0, len(CHARS)-1)])
    return output


def find_user_or_404(query: str):
    from .models import Profile
    try:
        return find_user(query)
    except Profile.DoesNotExist:
        raise Http404('Page does not exist.')


def find_user(query: str):
    from .models import Profile
    return Profile.objects.get(
        Q(username__iexact=query) | Q(email__iexact=query)
    )


def prepare_password_recovery(user_query: str):
    """
    Create PasswordRecovery model for related user
    and return user with created password recovery model
    """
    from .models import Profile, PasswordRecovery
    user = find_user(user_query)
    try:
        user.password_recovery.refresh()
    except PasswordRecovery.DoesNotExist:
        PasswordRecovery.objects.create(profile=user)
    return user


def generate_confirmation_html_email(token: str) -> str:
    return '''
    <h1>Chattings: Email confirmation</h1>

    <p>You see this email because someone used your email
    to registrate on <a href="http://localhost:8000">chattings.com</a>,
    if it\'s not you just ignore this message.</p>

    <p>Follow this link to confirm your email address:
    <a href="http://localhost:8000{0}">confirm</a></p>

    <p><a href="http://localhost:8000">chattings.com</a> | {1}</p>
    '''.format(
        reverse('users:email_confirmation', kwargs={
            'token': token
        }),
        timezone.now().year
    )


def generate_password_recovery_html_email(token: str) -> str:
    return '''
    <h1>Chattings: Password Recovery</h1>

    <p>You see this email because someone used your email
    to recover password on <a href="http://localhost:8000">chattings.com</a>,
    if it\'s not you just ignore this message.</p>

    <p>Follow this link to continue password recovery:
    <a href="http://localhost:8000{0}">recover password</a></p>

    <p><a href="http://localhost:8000">chattings.com</a> | {1}</p>
    '''.format(
        reverse('users:recover_password', kwargs={
            'token': token
        }),
        timezone.now().year
    )


def perform_email_verification(user, request:Optional=None,
    update_verification=False):
    """
    Creates EmailVerification model and send email verification letter

     Args:
       user - instance of user model which email need to be
              confirmed.
       
       update_verification - determines whether the verification
                     token needs to be updated.
       
       request - optional parameter which need to send messages
    """
    if update_verification: user.email_verification.refresh()
    
    html_message = generate_confirmation_html_email(user.email_verification.token)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject='Chattings: Confirm your email',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message)
    
    if request:
        success(request, ('We sent email confirmation'
            ' link to your email box. (Don\'t forget to check spam box)'),
            'success-registration')


def perform_password_recovery(email, request, alert:bool=True):
    """
    Alogorithm of preparing password recovery:
    1. Generate message which will be sent to user
    2. Send current message
    3. Tell to user in template about successfully
       sending email.
    """
    logout(request)
    user = prepare_password_recovery(email)

    html_message = generate_password_recovery_html_email(
        user.password_recovery.token)
    plain_message = strip_tags(html_message)

    send_mail(
        subject='Chattings: Recover your password',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message)

    if alert:
        success(request, ('Now check your email for'
            ' password recovery message.'),
            'pwd-recovery-mail-sent')


def force_confirm_email(token: str):
    """
    Force email confirmation: using when we want to confirm email
    without validation steps (for example like in confirm_email function).

     Args:
        token - token of EmailVerification model
    """
    try:
        from .models import EmailVerification
        can_login_permission = Permission.objects.get(codename='can_login')
        verification = EmailVerification.objects.get(token=token)
        verification.profile.user_permissions.add(can_login_permission)
        verification.delete()
    except EmailVerification.DoesNotExist:
        pass


def confirm_email(token: str, request):
    """
    Seeks out EmailVerification model with specific token and
    confirm email address of user which related for such
    EmailVerification model.
    """
    from .models import EmailVerification # due to a circular import
    can_login_permission = Permission.objects.get(codename='can_login')
    try:
        verification = EmailVerification.objects.get(token=token)
        # validation here
        if timezone.now() < verification.expiration_date:
            verification.profile.user_permissions.add(can_login_permission)
            success(request, 'Email successfully confirmed,'
                ' now you can login.', 'email-confirmed')
            verification.delete()
        else:
            error(request, 'EmailVerification expired.', 'token-expired')
    except EmailVerification.DoesNotExist:
        error(request, 'Invalid token. Make sure your'
            ' token is valid and not deleted.', 'invalid-token')


def recover_password(form, pwd_recovery_obj, request:Optional=None):
    """
    Algorithm:
    1. If user's email not confirmed then confirm it;
    2. Remove passed PasswordRecovery object;
    3. Save user model with changed data;
    """
    # step 1
    try:
        from .models import EmailVerification
        force_confirm_email(pwd_recovery_obj.profile.email_verification.token)
    except EmailVerification.DoesNotExist:
        pass
    # step 2
    pwd_recovery_obj.delete()
    # step 3
    form.save()

    if request:
        success(request, 'Password changed. You can login now.',
            'success-pwd-reset')
