from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username',
                    'is_active', 'recipe_count',
                    'subscription_count')
    search_fields = ('email', 'username')
    list_filter = ('is_active',)
    save_on_top = True

    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = 'Количество рецептов'

    def subscription_count(self, obj):
        return obj.follower.count()
    subscription_count.short_description = 'Количество подписок'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    save_on_top = True
