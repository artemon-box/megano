from django.urls import path
from .views import product_detail

app_name = "shopapp"

urlpatterns = [
    path('shop/products/<slug:product_slug>/', product_detail, name='product_detail'),
]
