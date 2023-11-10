from django.shortcuts import get_object_or_404
from rest_framework import serializers
# from rest_framework.validators import UniqueTogetherValidator
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Favorite,
    ShoppingCart
)
# from users.models import User, Follow
from users.serializers import UserGetSerializer


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
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, data):
        if Favorite.objects.filter(
            user=self.context['request'].user.id,
            recipe__id=data.id,
        ):
            return True
        else:
            return False

    def get_is_in_shopping_cart(self, data):
        if ShoppingCart.objects.filter(
            user=self.context['request'].user.id,
            recipe__id=data.id,
        ):
            return True
        else:
            return False


class RecipeSerializerPost(serializers.ModelSerializer):
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
            'cooking_time',
            'author'
        )

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
        print(instance)
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        instance.cooking_time = validated_data.pop('cooking_time')
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
        print(instance.ingredients)
        recipe = super(RecipeSerializerPost, self).to_representation(instance)
        # tags = [tag for tag in recipe['tags']]
        # recipe['tags'] = [Tag.objects.get(pk=tag) for tag in tags]
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
        representation['cooking_time'] = recipe.cooking_time
        representation.pop('user', None)
        representation.pop('recipe', None)
        return representation
