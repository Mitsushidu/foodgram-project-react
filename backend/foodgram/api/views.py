from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from recipes.models import Recipe, Tag, Ingredient
from .serializers import (
    RecipeSerializerPost,
    RecipeSerializerRead,
    TagSerializer,
    IngredientSerializer,
)
from .mixins import GetListCreateDestroyUpdateViewSet


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
