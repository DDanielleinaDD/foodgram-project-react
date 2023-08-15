from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


class IngredientAmountAdmin(admin.TabularInline):
    model = IngredientAmount
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientAmountAdmin,)
    list_display = ('pk', 'name',
                    'author', 'text',
                    'pub_date',)
    search_fields = ('name',
                     'author__username',
                     'text')
    list_filter = ('name', 'author__username', 'pub_date')
    empty_value_display = '-пусто-'
    list_per_page = 25
    save_on_top = True


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    save_on_top = True


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient',
                    'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    empty_value_display = '-пусто-'
    save_on_top = True


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name',
                    'color', 'slug')
    search_fields = ('name', 'color',
                     'slug')
    list_filter = ('name', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user',
                    'recipe')
    search_fields = ('user__username',)
    list_filter = ('user', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username',)
    list_filter = ('user', 'recipe__name')
