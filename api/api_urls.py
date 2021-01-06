#----------------------------------------------
# File with all api's urlspatterns in one place
#----------------------------------------------
from django.urls import path
from rest_framework.authtoken import views

from api.users.urls import urlpatterns as users_urlpatterns
from api.chats.urls import urlpatterns as chats_urlpatterns

urlpatterns = [
    path('token-auth/', views.obtain_auth_token, name='api-token-auth'),
]
urlpatterns += users_urlpatterns
urlpatterns += chats_urlpatterns
