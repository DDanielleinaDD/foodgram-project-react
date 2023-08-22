import os
from io import BytesIO

from django.conf import settings
from django.shortcuts import get_object_or_404
from recipe.models import Ingredient, IngredientAmount
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


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


def create_pdf(ingredients_in_cart):
    font_path = os.path.join(settings.BASE_DIR, 'fonts', 'Lineyka.ttf')
    pdfmetrics.registerFont(TTFont('Lineyka', font_path))
    buffer = BytesIO()
    docs = canvas.Canvas(buffer, pagesize=letter)
    docs.setFont('Lineyka', 12)
    docs.drawString(75, 750, 'Список ингредиентов:', mode=2)
    coord_y = 750
    count = 1
    for ingredient in ingredients_in_cart:
        name = ingredient['ingredient__name']
        unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['ingredient_amount']
        docs.drawString(80, coord_y - 25,
                        f'{count}) {name} - {amount}{unit}')
        count += 1
        coord_y -= 25
    docs.showPage()
    docs.save()

    buffer.seek(0)
    return buffer
