from django.contrib import admin
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'sort_index')
    list_filter = ('is_active',)
    search_fields = ('name',)


admin.site.register(Category, CategoryAdmin)
from shopapp.models import Product, ProductSeller


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'available']
    list_filter = ['available', 'category']
    search_fields = ['name', 'category']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['category']
    ordering = ['name', 'category']


@admin.register(ProductSeller)
class ProductSellerAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'seller', 'price', 'quantity']
