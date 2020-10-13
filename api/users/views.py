from rest_framework import viewsets

from .serializers import ProfileSerializer
from apps.users.models import Profile


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
