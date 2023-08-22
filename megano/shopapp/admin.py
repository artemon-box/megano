from django.contrib import admin

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
