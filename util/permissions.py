from rest_framework.permissions import BasePermission


class IClient(BasePermission):

    def has_permission(self, request, view):
        return hasattr(request.user,'client')

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)