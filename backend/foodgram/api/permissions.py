from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_staff
                or obj.author == request.user)


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in ['POST', 'GET'] or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated or request.method in ['GET']:
            return True


class RecipePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in ['GET'] or (
                request.user.is_authenticated
            )
        )

    def has_object_permission(self, request, view, obj):
        if request.method == 'POST' and (
            request.user.is_authenticated
        ):
            return True
        elif request.method in ['PUT', 'DELETE', 'PATCH'] and (
            request.user.is_authenticated
        ):
            return obj.author == request.user or request.user.is_staff
        elif request.method == 'GET':
            return True
