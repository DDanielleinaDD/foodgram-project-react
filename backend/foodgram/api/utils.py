from django.shortcuts import get_object_or_404

from recipe.models import Ingredient, IngredientAmount


def create_ingredients(ingredients, recipe):
    for ingredient in ingredients:
        ingredient_in_db = get_object_or_404(
            Ingredient, id=ingredient['id']
        )
        amount = ingredient['amount']
        IngredientAmount.objects.bulk_create([
            IngredientAmount(
                recipe=recipe,
                ingredient=ingredient_in_db,
                amount=amount,
            )
        ])
