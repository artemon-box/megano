from django.contrib import admin
from .models import Product, ProductSeller, Category, Seller


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'available']
    list_filter = ['available', 'category']
    search_fields = ['name', 'category']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name', 'category']


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'slug', 'description']
    list_filter = ['name', 'delivery_method', 'payment_method']
    search_fields = ['name',]
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name', 'delivery_method', 'payment_method']


@admin.register(ProductSeller)
class ProductSellerAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'seller', 'price', 'quantity']
