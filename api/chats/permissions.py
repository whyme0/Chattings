from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
