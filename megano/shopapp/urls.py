from django.urls import path

from . import views

from .views import HomeView, ProductDetailView, run_task, get_status, SellerDetailView, discount_list

app_name = "shopapp"

urlpatterns = [
    path("", HomeView.as_view(), name="index"),
    path("compare/", views.ComparisonOfProducts.as_view(), name="compare_list"),
    path(
        "compare/add/<int:product_id>/",
        views.AddToComparison.as_view(),
        name="compare_add",
    ),
    path(
        "compare/remove/<int:product_id>/",
        views.RemoveFromComparison.as_view(),
        name="compare_remove",
    ),
    path("compare/clear/", views.ClearComparison.as_view(), name="compare_clear"),
    path("catalog/", views.catalog_list, name="catalog_list"),
    path(
        "products/<slug:product_slug>/",
        ProductDetailView.as_view(),
        name="product_detail",
    ),
    path("discounts", discount_list, name="discounts"),
    path('tasks/', run_task, name='run_task'),
    path('tasks/<task_id>/', get_status, name='get_status'),
    path('sellers/<slug:seller_slug>/', SellerDetailView.as_view(), name='seller_detail'),
]
