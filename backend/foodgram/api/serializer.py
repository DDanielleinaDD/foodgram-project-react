from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipe.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                           ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow, User

from .utils import create_ingredients


class UserGetSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'id')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated
                and Follow.objects.filter(
                    user=user,
                    author=obj
                ). exists())


class UserSignUpSerializer(UserCreateSerializer):
    '''Сериализатор регистрации пользователя.'''
    class Meta:
        model = User
        fields = ('email', 'username',
                  'first_name', 'last_name',
                  'password')


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с краткой информацией о рецепте."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор для работы с тэгами.'''
    class Meta:
        model = Tag
        fields = ('id', 'name',
                  'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    ''''Сериализатор для ингредиентов.'''
    class Meta:
        model = Ingredient
        fields = ('__all__')


class IngredientAmountGetSerializer(serializers.ModelSerializer):
    '''Сериаализатор для отображения количества ингредиентов.'''
    id = serializers.IntegerField(source='ingredient.id',
                                  read_only=True)
    name = serializers.CharField(source='ingredient.name',
                                 read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name',
                  'measurement_unit', 'amount')


class IngredientAmountPostSerializer(serializers.ModelSerializer):
    '''Сериализатор для записи количества ингредиентов для рецепта.'''
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')

    def validate(self, attrs):
        amount = attrs['amount']
        if amount < 1:
            raise serializers.ValidationError(
                'Количество должно быть больше 0!'
            )
        if amount > 5000:
            raise serializers.ValidationError(
                'Количество не более 5000!'
            )
        return attrs


class FavoriteSerializer(serializers.ModelSerializer):
    '''Сериализатор для избранного.'''
    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [UniqueTogetherValidator(
            queryset=Favorite.objects.all(),
            fields=('user', 'recipe'),
            message='Рецепт уже в избранном.'
        )]

    def to_representation(self, instance):
        request = self.context['request']
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class RecipeGetSerializer(serializers.ModelSerializer):
    '''Сериализатор получения рецепта.'''
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    author = UserGetSerializer(
        read_only=True
    )
    ingredients = IngredientAmountGetSerializer(
        many=True,
        read_only=True,
        source='ingredientamount'
    )
    image = Base64ImageField(
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags',
                  'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image',
                  'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context['request']
        user = self.context['request'].user
        return (request and user.is_authenticated
                and Favorite.objects.filter(user=user,
                                            recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        user = self.context['request'].user
        return (request and user.is_authenticated
                and ShoppingCart.objects.filter(user=user,
                                                recipe=obj).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор создания рецепта.'''
    ingredients = IngredientAmountPostSerializer(
        source='ingredientamount',
        required=True,
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        required=True,
        many=True
    )
    image = Base64ImageField(
        required=True
    )
    cooking_time = serializers.IntegerField(
        required=True
    )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags',
                  'image', 'name',
                  'text', 'cooking_time')

    def validate(self, attrs):
        ingredients = attrs['ingredientamount']
        ingredients_list = []
        for ingredient in ingredients:
            if not Ingredient.objects.filter(
                    id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    f'Игридиента {ingredient["id"]} нет в базе!'
                )
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    f'Ингредиента {ingredient["id"]} - не может быть меньше 1!'
                )
            ingredients_list.append(ingredient['id'])
        if len(ingredients) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                'Вы указали повторяющиеся ингредиенты!'
            )

        tags = attrs['tags']
        tags_list = []
        if not tags:
            raise serializers.ValidationError(
                'Рецепт без тэга запрещен!'
            )
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Тэги не должны повторяться!'
                )
            tags_list.append(tag)

        cooking_time = attrs['cooking_time']
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть минимум 1 минута!'
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request']
        author = request.user
        ingredients = validated_data.pop('ingredientamount')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=author, **validated_data
        )
        recipe.tags.set(tags)
        create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_new = validated_data.pop('ingredientamount')
        instance.ingredients.clear()
        create_ingredients(ingredients_new, instance)
        tags_new = validated_data.pop('tags')
        instance.tags.set(tags_new)
        return super().update(instance,
                              validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetSerializer(
            instance,
            context={'request': request}
        ).data


class UserRecipesGetSerializer(UserGetSerializer):
    '''Промежуточный сериализатор для получения рецепта.'''
    recipes = RecipeGetSerializer()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class UserSubscriptionsGetSerializer(UserRecipesGetSerializer):
    '''Сериализатор для получения подписок пользователя
       и рецептов авторов.'''
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email',
                  'username', 'is_subscribed',
                  'first_name', 'last_name',
                  'recipes', 'recipes_count')
        read_only_fields = ('email',
                            'username', 'is_subscribed',
                            'first_name', 'last_name',
                            'recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context['request']
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeSmallSerializer(recipes, many=True,
                                     context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowCreateSerializer(serializers.ModelSerializer):
    '''Подписка на автора.'''
    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на данного автора.'
            )
        ]

    def validate(self, data):
        user = self.context['request'].user
        if user == data['author']:
            raise serializers.ValidationError(
                'Подписка на себя невозможна!'
            )
        return data

    def to_representation(self, instance):
        request = self.context['request']
        return UserSubscriptionsGetSerializer(
            instance.author, context={'request': request}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    '''Сериализатор для корзины покупок.'''
    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [UniqueTogetherValidator(
            queryset=ShoppingCart.objects.all(),
            fields=('user', 'recipe'),
            message='Продукты данного рецепта уже в вашей корзине.'
        )]

    def to_representation(self, instance):
        request = self.context['request']
        return RecipeSmallSerializer(
            instance.recipe,
            context={'request': request}
        ).data
