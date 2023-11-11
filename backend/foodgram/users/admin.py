from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Follow


@admin.register(Follow)
class PersonAdmin(admin.ModelAdmin):
    pass


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')


admin.site.register(User, UserAdmin)
