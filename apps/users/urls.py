from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    # Part for login, registration, passwords recovery, etc. views
    path(
        'auth/login/',
        views.UserLoginView.as_view(),
        name='login',
    ),
    
    path(
        'auth/registration/',
        views.UserRegistrationView.as_view(),
        name='registration',
    ),

    path(
        'auth/emailverification/<slug:token>',
        views.EmailConfirmationView.as_view(),
        name='email_confirmation',
    ),

    path(
        'auth/resend-confirmation-email/',
        views.ResendEmailConfirmation.as_view(),
        name='resend_confirmation_email',
    ),


    # Part specially for user, user settings, user data, etc.
    path(
        'profile/<slug:username>',
        views.ProfileView.as_view(),
        name='profile',
    )
]
