from django.contrib import admin
from django.contrib.auth import get_user_model


@admin.register(get_user_model())
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name',
                    'is_staff')
    search_fields = ('name', 'email')
    ordering = ('email',)

