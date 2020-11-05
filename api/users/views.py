from typing import Dict

from rest_framework import viewsets
from rest_framework import mixins

from .serializers import ProfileSerializer
from apps.users.models import Profile


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def _normalized_public_info(self) -> Dict[str, str]:
        public_info = self.get_object().privacy_settings.get_public_info()
        public_info = {k.lower().replace(' ', '_'): v.lower() for k,v in public_info.items()}
        return public_info

    def _update_serializer_fields(
        self,
        public_info: Dict[str, str],
        serializer_cls: serializer_class
        ) -> serializer_class:

        for field, value in public_info.items():
            if value != 'hidden' and field not in serializer_cls.Meta.fields:
                serializer_cls.Meta.fields.append(field)
        return serializer_cls
