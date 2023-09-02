from django.urls import path
from .views import index, ProductDetailView

app_name = "shopapp"

urlpatterns = [
    path('', index, name='index'),
    path('products/<slug:product_slug>/', ProductDetailView.as_view(), name='product_detail'),
]

