import base64
import imghdr
import uuid

import six
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import UserGetSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')
            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


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
    author = UserGetSerializer()
    ingredients = RecipeIngredientSerializerRead(
        source='recipe_ingredient',
        many=True,
    )
    tags = TagSerializer(
        many=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'name',
            'text',
            'cooking_time',
            'image',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, data):
        return Favorite.objects.filter(
            user=self.context['request'].user.id,
            recipe__id=data.id,
        ).exists()

    def get_is_in_shopping_cart(self, data):
        return ShoppingCart.objects.filter(
            user=self.context['request'].user.id,
            recipe__id=data.id,
        ).exists()


class RecipeSerializerPost(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None,
        use_url=True
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredient',
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = UserGetSerializer(
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'name',
            'text',
            'image',
            'cooking_time',
            'author'
        )

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('Empty tag list')
        lst_tags = []
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    'No such tag'
                )
            if tag in lst_tags:
                raise serializers.ValidationError(
                    'Tags must be unique'
                )
            lst_tags.append(tag)
        return tags

    def validate_ingredients(self, data):
        if not data:
            raise serializers.ValidationError('Empty tag list')
        ingredients = self.initial_data.get('ingredients')
        lst_ingredients = []
        for ingredient in ingredients:
            print(ingredients, ingredient)
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    'No such ingredient'
                )
            if ingredient in lst_ingredients:
                raise serializers.ValidationError(
                    'Ingredients must be unique'
                )
            lst_ingredients.append(ingredient)
        return ingredients

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        recipe.tags.set(tags)
        for ingredient in ingredients:
            recipe.ingredients.add(
                ingredient.get('id'),
                through_defaults={
                    'amount': ingredient.get('amount'),
                }
            )

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.pop('name', instance.name)
        instance.text = validated_data.pop('text', instance.text)
        instance.cooking_time = validated_data.pop(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.pop('image', instance.image)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredient')
        for tag in tags:
            if not RecipeTag.objects.filter(tag=tag, recipe=instance).exists():
                instance.tags.add(
                    tag.id,
                )
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id').id
            if not RecipeIngredient.objects.filter(
                ingredient=ingredient_id,
                recipe=instance
            ).exists():
                instance.ingredients.add(
                    ingredient_id,
                    through_defaults={
                        'amount': ingredient.get('amount'),
                    }
                )
        instance.save()
        return instance

    def to_representation(self, instance):
        recipe = super(RecipeSerializerPost, self).to_representation(instance)
        ingredients = RecipeIngredient.objects.filter(
            recipe=instance.id
        )
        ingredients_serializer = RecipeIngredientSerializerRead(
            ingredients,
            source='recipe_ingredient',
            many=True
        )
        tags_serializer = TagSerializer(
            Tag.objects.filter(pk__in=recipe['tags']),
            many=True
        )
        recipe['id'] = instance.id
        recipe['tags'] = tags_serializer.data
        recipe['ingredients'] = ingredients_serializer.data
        return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context['request'].user
        recipe = get_object_or_404(
            Recipe,
            id=self.context.get('view').kwargs.get('recipe_id')
        )
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError('Recipe is already in favorite')
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        recipe = get_object_or_404(
            Recipe,
            id=self.context.get('view').kwargs.get('recipe_id')
        )
        return Favorite.objects.create(
            recipe=recipe,
            user=user
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipe = instance.recipe
        representation['id'] = recipe.id
        representation['name'] = recipe.name
        representation['image'] = str(recipe.image)
        representation['cooking_time'] = recipe.cooking_time
        representation.pop('user', None)
        representation.pop('recipe', None)
        return representation


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        user = self.context['request'].user
        recipe = get_object_or_404(
            Recipe,
            id=self.context.get('view').kwargs.get('recipe_id')
        )
        if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                'Recipe is already in shopping cart'
            )
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        recipe = get_object_or_404(
            Recipe,
            id=self.context.get('view').kwargs.get('recipe_id')
        )
        return ShoppingCart.objects.create(
            recipe=recipe,
            user=user
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipe = instance.recipe
        representation['id'] = recipe.id
        representation['name'] = recipe.name
        representation['image'] = str(recipe.image)
        representation['cooking_time'] = recipe.cooking_time
        representation.pop('user', None)
        representation.pop('recipe', None)
        return representation
