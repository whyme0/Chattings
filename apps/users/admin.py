from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import Profile, EmailVerification, PasswordRecovery

admin.site.register(Profile)
admin.site.register(EmailVerification)
admin.site.register(PasswordRecovery)
