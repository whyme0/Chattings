from django.urls import path

from .views import ProfileViewSet

profile_list = ProfileViewSet.as_view({
    'get': 'list',
})
profile_detail = ProfileViewSet.as_view({
    'get': 'retrieve'
})

urlpatterns = [
    path('profiles/', profile_list, name='api-profiles'),
    path('profiles/<int:pk>/', profile_detail, name='api-profile'),
]