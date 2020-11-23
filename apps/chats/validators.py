from django.core.exceptions import ValidationError


def validate_empty_string(val):
    if len(val.split()) == 0:
        raise ValidationError("Field is empty.")
