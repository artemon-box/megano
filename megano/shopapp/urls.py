from django.urls import path
from .views import index, ProductDetailView
from shopapp.views import catalog_list

app_name = "shopapp"

urlpatterns = [
    path('', index, name='index'),
    path('catalog/', catalog_list, name='catalog_list'),
    path('products/<slug:product_slug>/', ProductDetailView.as_view(), name='product_detail'),
]
