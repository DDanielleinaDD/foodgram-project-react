import django_filters

from recipe.models import Ingredient, Recipe, Tag


class IngredientFilter(django_filters.FilterSet):
    '''Фильтр для поиска по ингредиентам.'''
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    '''Фильтр рецептов по тэгам, избранному и
       добавлению в корзину покупок.'''
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    is_favorited = django_filters.BooleanFilter(
        method='get_is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, name, queryset, value):
        if self.request.user.is_authenticated:
            if value:
                return (queryset.filter(favorite__user=self.request.user))
            return (queryset.exclude(favorite__user=self.request.user))
        return queryset.none()

    def get_is_in_shopping_cart(self, name, queryset, value):
        if self.request.user.is_authenticated:
            if value:
                return (queryset.filter(shoppingcart__user=self.request.user))
            return (queryset.exclude(shoppingcart__user=self.request.user))
        return queryset.none()
