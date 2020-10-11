from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path(
        'login/',
        views.UserLoginView.as_view(),
        name='login',
    ),
    
    path(
        'registration/',
        views.UserRegistrationView.as_view(),
        name='registration',
    ),

    path(
        'emailverification/<slug:token>',
        views.EmailConfirmationView.as_view(),
        name='email_confirmation',
    ),

    path(
        'resend-confirmation-email/',
        views.ResendEmailConfirmation.as_view(),
        name='resend_confirmation_email',
    ),
]
