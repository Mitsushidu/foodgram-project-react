from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Recipe

from .models import Follow, User


class UserRegistrationSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.id
        return representation


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, data):
        return Follow.objects.filter(
            user=self.context['request'].user.id,
            author=data.id,
        ).exists()


class RecipeUserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta():
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionListSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, data):
        recipes_limit = self.context['request'].GET.get('recipes_limit', '')
        query = Recipe.objects.filter(author=data.id)
        if recipes_limit != '':
            query = query[:int(recipes_limit)]
        serializer = RecipeUserSubscriptionSerializer(
            query,
            many=True
        )
        return serializer.data

    def get_is_subscribed(self, data):
        return Follow.objects.filter(
            user=self.context['request'].user.id,
            author=data.id,
        ).exists()

    def get_recipes_count(self, data):
        return Recipe.objects.filter(author=data.id).count()
