from django.urls import path

from .views import ProfileViewSet

profile_detail = ProfileViewSet.as_view({
    'get': 'retrieve'
})

urlpatterns = [
    path('profiles/<int:pk>/', profile_detail, name='api-profile'),
]