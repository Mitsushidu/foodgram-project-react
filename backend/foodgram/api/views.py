from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import HttpResponse
from djoser.serializers import SetPasswordSerializer
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)
from users.models import User, Follow
from users.serializers import (
    UserGetSerializer,
    UserRegistrationSerializer,
    SubscriptionListSerializer
)
from .serializers import (
    RecipeSerializerPost,
    RecipeSerializerRead,
    TagSerializer,
    IngredientSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
)
from .mixins import (
    GetListCreateDestroyUpdateViewSet,
    GetListCreateViewSet,
    CreateDestroyViewSet,
)
from .permissions import (
    UserPermission,
)


class RecipeViewSet(GetListCreateDestroyUpdateViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializerRead
        else:
            return RecipeSerializerPost

    @action(methods=['get'], detail=False, url_path=r'download_shopping_cart')
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
        print(ingredients)
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
        with open('shopping_cart.txt', 'w', encoding='utf-8') as file:
            for lst in ingredient_dict.values():
                file.write(f'{lst[0]} ({lst[1]}) — {lst[2]}\n')
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class UserViewSet(GetListCreateViewSet):
    queryset = User.objects.all()
    permission_classes = (UserPermission,)

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
        user = request.user
        serializer = UserGetSerializer(
            user,
            context={'request': request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path=r'subscriptions')
    def subscriptions(self, request):
        subs = Follow.objects.filter(
            user=request.user
        ).values_list('author_id')
        user = User.objects.filter(pk__in=subs)
        serializer = SubscriptionListSerializer(
            user,
            context={'request': request},
            many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post', 'delete'], detail=True, url_path=r'subscribe')
    def subscriptions(self, request, pk=None):
        subscriber = request.user
        author = self.get_object()
        print(author.id)
        if request.method == 'POST':
            if Follow.objects.filter(
                user=subscriber,
                author=author,
            ):
                return Response(
                    {'error': 'Subscription already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif author == subscriber:
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
        if request.method == 'DELETE':
            if not Follow.objects.filter(
                user=subscriber,
                author=author,
            ):
                return Response(
                    {'error': 'Subscription doesn\'t exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.get(
                user=subscriber,
                author=author,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(CreateDestroyViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ShoppingCartViewSet(CreateDestroyViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    def delete(self, request, recipe_id=None):
        user = request.user
        recipe = Recipe.objects.get(id=recipe_id)
        if not ShoppingCart.objects.filter(
            user=user,
            recipe=recipe,
        ):
            return Response(
                {'error': 'Subscription doesn\'t exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            ShoppingCart.objects.get(
                user=user,
                recipe=recipe,
            ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
