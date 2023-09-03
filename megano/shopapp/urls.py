from django.urls import path
from . import views


app_name = "shopapp"

urlpatterns = [
    path('compare/', views.ComparisonOfProducts.as_view(), name='compare_list'),
    path('compare/add/<int:product_id>/', views.AddToComparison.as_view(), name='compare_add'),
    path('compare/remove/<int:product_id>/', views.RemoveFromComparison.as_view(), name='compare_remove'),
    path('catalog/', views.catalog_list, name='catalog_list'),
]
