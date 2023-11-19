from django.contrib import admin

from .models import Follow, User


@admin.register(Follow)
class PersonAdmin(admin.ModelAdmin):
    pass


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')


admin.site.register(User, UserAdmin)
