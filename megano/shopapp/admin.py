from django.contrib import admin
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'sort_index')
    list_filter = ('is_active',)
    search_fields = ('name',)


admin.site.register(Category, CategoryAdmin)
