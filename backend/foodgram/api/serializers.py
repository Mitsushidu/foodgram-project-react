from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.relations import SlugRelatedField
from recipes.models import Ingredient, Tag, Recipe, Follow

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

