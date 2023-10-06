from django.urls import path
from .views import HistProductsView

app_name = "histviewapp"

urlpatterns = [
    path('products/', HistProductsView.as_view(), name='products'),
]
