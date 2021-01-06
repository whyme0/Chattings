from django.core.exceptions import ValidationError


def validate_empty_string(val):
    if len(val.split()) == 0:
        raise ValidationError("Field is empty.")

def file_size_validator(self):
    # If size > 10Mb
    if img.file.size > 1024 * 1024 * 10:
        raise ValidationError('This file too large.')
