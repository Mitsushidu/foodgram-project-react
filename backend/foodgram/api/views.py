from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from recipes.models import Recipe, Tag, Ingredient
from .serializers import (
    RecipeSerializerPost,
    TagSerializer,
    IngredientSerializer,
)
from .mixins import GetListCreateDestroyUpdateViewSet


class RecipeViewSet(GetListCreateDestroyUpdateViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerPost


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
