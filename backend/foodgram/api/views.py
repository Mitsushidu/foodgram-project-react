from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Favorite,
    ShoppingCart
)
from users.models import User, Follow
from users.serializers import (
    UserGetSerializer,
    SubscriptionListSerializer,
    SubscribeSerializer
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
    GetListViewSet,
    CreateDestroyViewSet,
)


class RecipeViewSet(GetListCreateDestroyUpdateViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializerRead
        else:
            return RecipeSerializerPost


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class UserViewSet(GetListViewSet):
    queryset = User.objects.all()
    serializer_class = UserGetSerializer

    @action(methods=['get'], detail=False, url_path=r'subscriptions')
    def subscriptions(self, request):
        subs = Follow.objects.filter(user=request.user).values_list('author_id')
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
