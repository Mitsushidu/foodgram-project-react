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


@admin.register(RecipeTag,
                RecipeIngredient,
                )
class PersonAdmin(admin.ModelAdmin):
    pass


class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']
    search_fields = ['name', ]
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    list_filter = ['user', 'recipe']
    search_fields = ['user', 'recipe']
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'user']
    list_filter = ['recipe', 'user']
    search_fields = ['user', ]
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ['author', 'name', 'tags']
    list_display = ['name', 'author', 'favorite_count']

    @admin.display(description="Число добавлений в избранное")
    def favorite_count(self, obj):
        favorite_count = Favorite.objects.filter(recipe=obj).count()
        return favorite_count


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ['name', 'measurement_unit']
    search_fields = ['name', ]
    list_display = ['name', ]


admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
