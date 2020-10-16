from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.db.models import Q


def username_exist_validator(val):
    """
    Help to determine is exist user with specific username or email.
    """
    try:
        get_user_model().objects.get(Q(username=val) | Q(email=val))
    except get_user_model().DoesNotExist:
        msg = 'User with this username doesn\'t exist.'
        if '@' in val:
            msg = 'User with this email doesn\'t exist.'
        
        raise ValidationError(msg)


class UsernameRegexValidator(RegexValidator):
    regex=r'^[\w-]+\Z'
    message=(
        'Enter valid username. This value may contain only letters, '
        'numbers, and -/_ characters.'
    )
    flags=0
