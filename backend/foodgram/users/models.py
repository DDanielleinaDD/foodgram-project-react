from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    '''Модель пользователя.'''
    email = models.CharField(
        verbose_name='Почта пользователя',
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Юзернейм пользователя',
        max_length=settings.MAX_LENGTH_OTHER,
        unique=True,
        validators=(validate_username,)
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.MAX_LENGTH_OTHER,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=settings.MAX_LENGTH_OTHER,
        blank=True
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=settings.MAX_LENGTH_OTHER,
    )
    is_active = models.BooleanField(
        verbose_name='Доступ пользователя',
        default=True,
    )

    class Meta:
        ordering = ('-username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    '''Модель подписки на другого пользователя.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_author'
            ),
            models.CheckConstraint(
                name='Подписка на себя невозможна',
                check=~models.Q(author=models.F('user'))
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username} - {self.author.username}'
