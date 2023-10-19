import json

from django.contrib import admin
from django.contrib.admin import forms
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import path
from taggit.models import Tag

from .forms import FileImportForm, ProductFeatureForm
from .models import (
    AllowedRelation,
    Category,
    Discount,
    ExtraImage,
    Feature,
    FeatureValue,
    Product,
    ProductFeature,
    ProductReview,
    ProductSeller,
    Seller,
)
from .views import ImportProducts


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    # filter_horizontal = ('sub_categories',)


class ExtraImageInline(admin.StackedInline):
    model = ExtraImage
    extra = 3


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    form = ProductFeatureForm
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "category",
        "slug",
        "available",
        "created_at",
        "popularity",
    ]
    list_filter = ["available", "category"]
    search_fields = ["name", "category"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name", "category"]
    inlines = [ExtraImageInline, ProductFeatureInline]


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "slug", "description"]
    list_filter = ["name", "delivery_method", "payment_method"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name", "delivery_method", "payment_method"]


@admin.action(description="Add limited edition product")
def mark_limited_edition(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(is_limited_edition=True)


@admin.action(description="Exclude a product from a limited edition")
def unmark_limited_edition(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(is_limited_edition=False)


@admin.register(ProductSeller)
class ProductSellerAdmin(admin.ModelAdmin):
    change_list_template = "shopapp/productsellers_changelist.html"
    actions = [
        mark_limited_edition,
        unmark_limited_edition,
    ]
    list_display = (
        "id",
        "product",
        "seller",
        "price",
        "free_delivery",
        "quantity",
        "is_limited_edition",
    )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []  # Суперпользователи могут редактировать все поля
        else:
            return ['seller']  # Обычные пользователи не могут редактировать эти поля

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-json",
                ImportProducts.as_view(),
                name="import_products_json",
            ),
        ]
        return new_urls + urls

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(ProductSellerAdmin, self).get_queryset(request)
        seller = Seller.objects.filter(user=request.user).first()
        return ProductSeller.objects.filter(seller=seller)


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
    list_display = [
        "product",
        "category",
        "feature",
        "value",
    ]


@admin.register(AllowedRelation)
class AllowedRelationAdmin(admin.ModelAdmin):
    list_display = [
        "category",
        "feature",
        "value",
    ]
    list_filter = ["category", "feature"]


@admin.action(description="Activate discount")
def mark_activate(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(is_active=True)


@admin.action(description="Deactivate discount")
def mark_deactivate(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(is_active=False)


@admin.register(Discount)
class ProductDiscountAdmin(admin.ModelAdmin):
    actions = [
        mark_activate,
        mark_deactivate,
    ]
    list_display = (
        "title",
        "type",
        "weight",
        "percent",
        "discount_volume",
        "cart_numbers",
        "cart_price",
        "start",
        "end",
        "is_active",
        "category_list",
        "product_list",
    )
    list_filter = ("title", "percent", "discount_volume", "cart_numbers", "cart_price", "start", "end")
    search_fields = ("title", "percent", "discount_volume", "cart_numbers", "cart_price", "start", "end")

    class Media:
        # css = {
        #     'all': ('css/admin/style.css', 'assets/css/hello_world.css',)
        # }
        js = ("assets/js/discount.js",)

    def product_list(self, obj):
        if obj.products.all():
            return list(obj.products.all())
        else:
            return "-"

    def category_list(self, obj):
        if obj.categories.all():
            return list(obj.categories.all().values_list("name", flat=True))
        else:
            return "-"
