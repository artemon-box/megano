from django.contrib import admin
from django.contrib.auth import get_user_model


@admin.register(get_user_model())
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_verified', 'first_name', 'last_name',
                    'is_staff')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)

