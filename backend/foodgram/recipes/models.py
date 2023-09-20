from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=200)
    measurement_unit = models.CharField('Единица измерения')


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=200, unique=True)
    slug = models.SlugField('Слаг тега', unique=True, max_length=200)
    color = models.CharField('Цвет', unique=True, max_length=7)


class Recipe(models.Model):
    name = models.CharField('Название рецепта', max_length=200)
    text = models.TextField()
    cooking_time = models.IntegerField('Время приготовления')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        through='RecipeIngredient'
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        through='RecipeTag'
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingridient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField('Количество')


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


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
