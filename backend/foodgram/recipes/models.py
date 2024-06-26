from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=32)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=200, unique=True)
    slug = models.SlugField('Слаг тега', unique=True, max_length=200)
    color = models.CharField('Цвет', unique=True, max_length=7)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField('Название рецепта',
                            max_length=200)
    text = models.TextField()
    image = models.ImageField('Изображение',
                              upload_to='recipes/image/',
                              )
    cooking_time = (
        models.PositiveSmallIntegerField(
            'Время приготовления',
            validators=[
                MinValueValidator(
                    1,
                    'Минимальное время готовки не менее одной минуты'
                )
            ]
        )
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        through='RecipeTag',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['text', 'author'],
                name='unique_text_author'
            )
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredient'
                               )
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='ingredient_recipe'
                                   )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                1,
                'Минимальное время готовки не менее одной минуты'
            )
        ]
    )

    def __str__(self):
        return f'{self.recipe} содержит {self.ingredient}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tag',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_recipe',
    )

    def __str__(self):
        return f'{self.recipe} имеет тег {self.tag}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_recipe',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_recipe_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_cart',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe} в корзине у {self.user}'
