from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class ReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in ['POST', 'GET']
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return True


class RecipePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in ['GET'] or (
                request.user.is_authenticated
            )
        )

    def has_object_permission(self, request, view, obj):
        if request.method == 'POST' and request.user.is_authenticated:
            return True
        elif request.method in ['PUT', 'DELETE'] and (
            request.user.is_authenticated
        ):
            return obj.author == request.user
        elif request.method == 'GET':
            return True
