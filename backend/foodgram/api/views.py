from rest_framework.viewsets import ReadOnlyModelViewSet
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Favorite,
    ShoppingCart
)
from users.models import User, Follow
from users.serializers import UserGetSerializer
from .serializers import (
    RecipeSerializerPost,
    RecipeSerializerRead,
    TagSerializer,
    IngredientSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer
)
from .mixins import (
    GetListCreateDestroyUpdateViewSet,
    GetListViewSet,
    CreateDestroyViewSet
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


class FavoriteViewSet(CreateDestroyViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ShoppingCartViewSet(CreateDestroyViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
