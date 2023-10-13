from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.relations import SlugRelatedField
from recipes.models import Ingredient, Tag, Recipe, Follow, RecipeIngredient, RecipeTag

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'color', 'slug')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    pass


class RecipeSerializerPost(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        print(tags, ingredients)
        for ingredient in ingredients:
            print(ingredient)
            RecipeIngredient.objects.create(
                ingredient=ingredient['ingredient'],
                recipe=recipe,
                amount=ingredient['amount'],
            )

        for tag in tags:
            print(tag)
            RecipeTag.objects.create(
                tag=tag['tag'],
                recipe=recipe,
            )

        return recipe