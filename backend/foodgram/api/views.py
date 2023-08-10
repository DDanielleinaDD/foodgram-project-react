import os

from io import BytesIO

from django.db.models import Sum
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipe.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                           ShoppingCart, Tag)
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import AdminAuthorOrReadOnly
from .serializer import (FavoriteSerializer, FollowCreateSerializer,
                         IngredientSerializer, RecipeCreateSerializer,
                         RecipeGetSerializer, ShoppingCartSerializer,
                         TagSerializer, UserSubscriptionsGetSerializer)


class UserFollowView(APIView):
    '''Подписка и отписка пользователя на автора.'''
    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        serializer = FollowCreateSerializer(
            data={'user': request.user.id,
                  'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        if Follow.objects.filter(user=request.user,
                                 author=author).exists():
            Follow.objects.get(user=request.user.id,
                               author=user_id).delete()
            return Response(data='Усешно отписались от пользователя!',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(data='errors: Запрос с ошибкой',
                        status=status.HTTP_400_BAD_REQUEST)


class UserFollowViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    '''Получение подписок пользователя.'''
    serializer_class = UserSubscriptionsGetSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Работа с тэгами.'''
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Работа с ингредиентами.'''
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    '''Работа с рецептами.'''
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (AdminAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id,
                      'recipe': recipe.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        if Favorite.objects.filter(user=request.user,
                                   recipe=recipe).exists():
            Favorite.objects.filter(user=request.user,
                                    recipe=recipe).delete()
            return Response(data='Рецепт успешно удален из корзины!',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(data={'errors': 'Этого рецепта нет в избранном!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id, },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if ShoppingCart.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            ShoppingCart.objects.filter(user=request.user,
                                        recipe=recipe).delete()
            return Response(data='Рецепт успешно удален!',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(data='Этого рецепта нет в корзине!',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        font_path = os.path.join(settings.BASE_DIR1, 'fonts', 'Lineyka.ttf')
        ingredients_in_cart = IngredientAmount.objects.filter(
            recipe__cart__user=request.user).values(
                        'ingredient__name',
                        'ingredient__measurement_unit').annotate(
                            ingredient_amount=Sum('amount'))
        print(ingredients_in_cart)
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
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = ('attachement;'
                                           'filename="ingredients.pdf"')
        return response
