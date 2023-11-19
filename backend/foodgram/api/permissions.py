from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in ['POST', 'GET'] or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated or (
            request.method in permissions.SAFE_METHODS
        )


class RecipePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or (
                request.user.is_authenticated
            )
        )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff or (
            request.method in permissions.SAFE_METHODS
        )
