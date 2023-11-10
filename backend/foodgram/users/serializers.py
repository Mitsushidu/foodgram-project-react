from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import Follow, User
from recipes.models import Recipe


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
        if Follow.objects.filter(
            user=self.context['request'].user.id,
            author=data.id,
        ):
            return True
        else:
            return False


class RecipeUserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta():
        model = Recipe
        fields = (
            'id',
            'name',
            'cooking_time'
        )


class SubscriptionListSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeUserSubscriptionSerializer(
        many=True,
        read_only=True
    )

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

    def get_is_subscribed(self, data):
        print(self.context)
        if Follow.objects.filter(
            user=self.context['request'].user.id,
            author=data.id,
        ):
            return True
        else:
            print(data)
            return False

    def get_recipes_count(self, data):
        return Recipe.objects.filter(author=data.id).count()


class SubscribeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = (
            'id',
        )

    def create(self, data):
        print(data.pk)
        author = data.author
        subscriber = self.context['request'].user.id
        print(author, subscriber)
        if Follow.objects.filter(
            user=subscriber,
            author=author,
        ):
            return serializers.ValidationError('Already subscribed')
        elif author == subscriber:
            return serializers.ValidationError('Can\'t subscribe to yourself')
        else:
            Follow.objects.create(
                user=subscriber,
                author=author,
            )
