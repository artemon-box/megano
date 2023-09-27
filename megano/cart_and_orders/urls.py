from django.urls import path
from .views import CartView, AddToCartView, RemoveFromCartView, ChangeCountInCartView

app_name = "cart_and_orders"

urlpatterns = [
    path('', CartView.as_view(), name='cart_view'),
    path('add/<str:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('change_quantity/<int:product_id>/', ChangeCountInCartView.as_view(), name='change_cart_quantity'),
    path('remove/<int:product_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
]
