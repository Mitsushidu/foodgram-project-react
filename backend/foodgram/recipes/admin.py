from django.contrib import admin
from .models import (
    Recipe,
    RecipeIngredient,
    RecipeTag,
    Tag,
    Ingredient,
    Favorite,
    ShoppingCart,
)


@admin.register(Recipe, RecipeTag, RecipeIngredient, Tag, Ingredient, Favorite, ShoppingCart)
class PersonAdmin(admin.ModelAdmin):
    pass
