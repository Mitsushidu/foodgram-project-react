from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow, User
from users.serializers import (SubscriptionListSerializer, UserGetSerializer,
                               UserRegistrationSerializer)

from .filters import IngredientFilter, RecipeFilter
from .mixins import (CreateDestroyViewSet, GetListCreateDestroyUpdateViewSet,
                     GetListCreateViewSet)
from .pagination import PageLimitPagination
from .permissions import RecipePermission, UserPermission
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializerPost, RecipeSerializerRead,
                          ShoppingCartSerializer, TagSerializer)


class RecipeViewSet(GetListCreateDestroyUpdateViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (RecipePermission,)
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializerRead
        else:
            return RecipeSerializerPost

    @action(methods=['get'],
            detail=False,
            url_path=r'download_shopping_cart',
            permission_classes=(permissions.IsAuthenticated, )
            )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(
            user=user
        ).values_list('recipe_id')
        recipes = Recipe.objects.filter(
            pk__in=shopping_cart
        )
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes
        )
        ingredient_dict = {}
        for recipeingredient in ingredients:
            ingredient = Ingredient.objects.get(
                id=recipeingredient.ingredient_id
            )
            data = [
                ingredient.name,
                ingredient.measurement_unit,
                recipeingredient.amount
            ]
            if ingredient.name in ingredient_dict:
                ingredient_dict[ingredient.name][2] += data[2]
            else:
                ingredient_dict[ingredient.name] = data
        shopping_list = ''
        for lst in ingredient_dict.values():
            shopping_list += (f'{lst[0]} ({lst[1]}) — {lst[2]}\n')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter, )
    search_fields = ('^name', )


class UserViewSet(GetListCreateViewSet):
    queryset = User.objects.all()
    permission_classes = (UserPermission,)
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.action in ['list', 'get']:
            return UserGetSerializer
        else:
            return UserRegistrationSerializer

    @action(["post"],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,)
            )
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'],
            detail=False,
            url_path=r'me',
            permission_classes=(permissions.IsAuthenticated,)
            )
    def me(self, request):
        serializer = UserGetSerializer(
            request.user,
            context={'request': request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'],
            detail=False,
            url_path=r'subscriptions',
            permission_classes=(permissions.IsAuthenticated,),
            )
    def subscriptions(self, request):
        subs = Follow.objects.filter(
            user=request.user
        ).values_list('author_id')
        users = User.objects.filter(
            pk__in=subs
        )
        page = self.paginate_queryset(users)
        if page is not None:
            return self.get_paginated_response(SubscriptionListSerializer(
                page,
                context={'request': request},
                many=True
            ).data)
        return Response(SubscriptionListSerializer(
            users,
            context={'request': request},
            many=True
        ).data, status=status.HTTP_200_OK)

    @action(methods=['post'],
            detail=True,
            url_path=r'subscribe',
            permission_classes=(permissions.IsAuthenticated,),
            )
    def subscription(self, request, pk=None):
        subscriber = request.user
        author = self.get_object()
        if Follow.objects.filter(
            user=subscriber,
            author=author,
        ).exists():
            return Response(
                {'error': 'Subscription already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if author == subscriber:
            return Response(
                {'error': 'Can\'t subscribe to yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(
            user=subscriber,
            author=author,
        )
        response = SubscriptionListSerializer(
            author,
            context={'request': request}
        )
        return Response(response.data, status=status.HTTP_201_CREATED)

    @subscription.mapping.delete
    def delete_subscription(self, request, pk=None):
        subscriber = request.user
        author = self.get_object()
        if not Follow.objects.filter(
            user=subscriber,
            author=author,
        ).exists():
            return Response(
                {'error': 'Subscription doesn\'t exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.get(
            user=subscriber,
            author=author,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def favorite_shopping_cart_delete(obj_class, user, recipe):
    if not obj_class.objects.filter(
            user=user,
            recipe=recipe,
    ).exists():
        return Response(
            {'error': 'No such recipe in list'},
            status=status.HTTP_400_BAD_REQUEST
        )
    obj_class.objects.get(
        user=user,
        recipe=recipe,
    ).delete()


class FavoriteViewSet(CreateDestroyViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, recipe_id=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite_shopping_cart_delete(Favorite, user, recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateDestroyViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, recipe_id=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite_shopping_cart_delete(ShoppingCart, user, recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)
