from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import validate_username


class User(AbstractUser):

    username = models.TextField(
        max_length=150,
        validators=(validate_username,),
        unique=True
    )
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(max_length=254, unique=True)
    # favorite = models.ManyToManyField(
    #     'recipes.Recipe',
    #     verbose_name='Избранное',
    #     through='recipes.Favorite',
    #     default=None,
    # )
    # shopping_cart = models.ManyToManyField(
    #     'recipes.Recipe',
    #     related_name='shopping_cart',
    #     through='recipes.ShoppingCart',
    #     default=None,
    # )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
