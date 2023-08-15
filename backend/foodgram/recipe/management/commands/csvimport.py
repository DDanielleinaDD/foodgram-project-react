import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from recipe.models import Ingredient


class Command(BaseCommand):
    '''Загрузка ингредиентов в БД.'''
    def handle(self, *args, **options):
        csv_file_path = os.path.join(settings.BASE_DIR1,
                                     'data', 'ingredients.csv')
        with open(
            csv_file_path,
            'r',
            encoding='utf-8'
        ) as csv_file:
            reader = csv.DictReader(csv_file, fieldnames=['name',
                                                          'measurement_unit'])
            try:
                Ingredient.objects.bulk_create(
                    Ingredient(**items) for items in reader
                )
            except IntegrityError:
                return 'Такие ингредиенты уже есть...'
        return (
            f'{Ingredient.objects.count()} - ингредиентов успешно загружено')
