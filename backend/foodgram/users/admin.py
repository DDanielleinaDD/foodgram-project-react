from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username',
                    'is_active')
    search_fields = ('email', 'username')
    list_filter = ('is_active',)
    save_on_top = True


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    save_on_top = True
