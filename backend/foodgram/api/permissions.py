from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or (
                request.method == 'POST')
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated


class RecipePermission(permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or (
            request.user.is_staff or request.user.is_superuser) or (
            request.method in permissions.SAFE_METHODS
        )
