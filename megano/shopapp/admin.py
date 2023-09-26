import json

from django.contrib import admin
from django.contrib.admin import forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from taggit.models import Tag
from django.urls import path
from .forms import ProductFeatureForm, FileImportForm

from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    #filter_horizontal = ('sub_categories',)


class ExtraImageInline(admin.StackedInline):
    model = ExtraImage
    extra = 3


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    form = ProductFeatureForm
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'slug', 'available', 'created_at', 'popularity']
    list_filter = ['available', 'category']
    search_fields = ['name', 'category']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name', 'category']
    inlines = [ExtraImageInline, ProductFeatureInline]


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'slug', 'description']
    list_filter = ['name', 'delivery_method', 'payment_method']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name', 'delivery_method', 'payment_method']


@admin.register(ProductSeller)
class ProductSellerAdmin(admin.ModelAdmin):
    change_list_template = 'shopapp/productsellers_changelist.html'
    list_display = ('id', 'product', 'seller', 'price', 'free_delivery', 'quantity')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('import-products-json', self.import_json, name='import_products_json',),
        ]
        return new_urls + urls

    def import_json(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = FileImportForm()
            context = {'form': form, 'header': 'Upload from JSON file'}
            return render(request, 'admin_settings/upload_file_form.html', context)
        form = FileImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {'form': form, 'header': 'Upload from JSON file'}
            return render(request, 'admin_settings/upload_file_form.html', context, status=400)

        products_from_json = json.load(form.files['file'])

        for product in products_from_json:
            ProductSeller.objects.create(
                prduct=Product.objects.get(id=product['product']),
                seller=Seller.objects.get(id=product['seller']),
                price=product['price'],
                quantity=product['quantity'],
            )

        self.message_user(request, "Data from JSON was imported")
        return redirect('..')


admin.site.register(ExtraImage)
admin.site.register(ProductReview)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    pass


@admin.register(FeatureValue)
class FeatureValueAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductFeature)
class ProductFeatureAdmin(admin.ModelAdmin):
    form = ProductFeatureForm
    list_display = ['product', 'category', 'feature', 'value', ]


@admin.register(AllowedRelation)
class AllowedRelationAdmin(admin.ModelAdmin):
    list_display = ['category', 'feature', 'value', ]
    list_filter = ['category', 'feature']
