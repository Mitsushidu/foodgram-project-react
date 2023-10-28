from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.relations import SlugRelatedField
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Favorite,
    ShoppingCart
)
from users.models import User, Follow


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeTagSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all()
    )

    class Meta:
        model = RecipeTag
        fields = ('id',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = RecipeTagSerializer(instance.id).data
        return ret


class RecipeIngredientSerializerRead(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='ingredient.id',
    )
    name = serializers.CharField(
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializerRead(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    ingredients = RecipeIngredientSerializerRead(
        source='recipe_ingredient',
        many=True,
    )
    tags = TagSerializer(
        many=True,
    )
    is_favorited = serializers.BooleanField(write_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'name',
            'text',
            'cooking_time',
            'author',
            'is_favorited',
        )

    def get_is_favorited(self, data):
        if Favorite.objects.filter(
            user=data['author'],
            recipe__id=data['id'],
        ):
            return True


class RecipeSerializerPost(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredient',
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def create(self, validated_data):
        print(validated_data)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            recipe.ingredients.add(
                ingredient.get('id'),
                through_defaults={
                    'amount': ingredient.get('amount'),
                }
            )

        return recipe
