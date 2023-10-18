from django.urls import path

from .views import (
    AddToCartView,
    CartView,
    ChangeCountInCartView,
    ClearCartView,
    OrderConfirmView,
    OrderView,
    RemoveFromCartView,
)

app_name = "cart_and_orders"

urlpatterns = [
    path("", CartView.as_view(), name="cart_view"),
    path("add/<str:product_id>/", AddToCartView.as_view(), name="add_to_cart"),
    path("change_quantity/<int:product_id>/", ChangeCountInCartView.as_view(), name="change_cart_quantity"),
    path("remove/<int:product_id>/", RemoveFromCartView.as_view(), name="remove_from_cart"),
    path("clear/", ClearCartView.as_view(), name="clear_cart"),
    path("order/", OrderView.as_view(), name="order"),
    path("order/confirm", OrderConfirmView.as_view(), name="order_confirm"),
]
