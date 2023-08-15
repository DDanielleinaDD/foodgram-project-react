from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    '''Модель инрегдиентов.'''
    name = models.CharField(max_length=256,
                            verbose_name='Название ингридиента')
    measurement_unit = models.CharField(max_length=54,
                                        verbose_name='Мера измерения')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique ingredient name"
            )
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    '''Модель тэга для рецепта.'''
    name = models.CharField(
        verbose_name='Название тега',
        max_length=24,
        unique=True
    )
    color = ColorField(
        verbose_name='Цвет тэга',
        max_length=24,
        unique=True
    )
    slug = models.CharField(
        verbose_name='Сокращенное название тэга',
        max_length=24,
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('-name',)

    def __str__(self):
        return (f'{self.name} - {self.color}')


class Recipe(models.Model):
    '''Модель рецепта.'''
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время создания рецепта',
        auto_now_add=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления(в минутах)',
        validators=[
            MinValueValidator(
                1, 'Время не может быть меньше 1 минуты.'
            )
        ]
    )
    image = models.ImageField(
        verbose_name='Изображения рецепта',
        upload_to='media/',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты для рецепта',
        related_name='recipes',
        through='IngredientAmount'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэш рецепта',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author} - {self.name}'


class Abstract(models.Model):
    '''Абстрактная модель для классов
       Favorite и ShoppingCart.'''
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Автор-Рецепт',
    )

    class Meta:
        abstract = True


class Favorite(Abstract):
    '''Модель избранного.'''

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('-user',)

    def __str__(self):
        return f'{self.user.username} add in favorites {self.recipe.name}'


class ShoppingCart(Abstract):
    '''Модель корзины покупок.'''

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('-user',)

    def __str__(self):
        return (f'{self.user.username} добавил в список покупок -'
                f'{self.recipe.name}')


class IngredientAmount(models.Model):
    '''Модель для работы с количеством ингредиентов.'''
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredientamount',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингрeдиенты',
        related_name='ingredientamount',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
        validators=[
            MinValueValidator(
                1, 'Количество ингредиента не менее 1.'
            ),
            MaxValueValidator(
                5000, 'Количество ингредиентов не более 5000.'
            )
        ]
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('-recipe__name',)

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'
