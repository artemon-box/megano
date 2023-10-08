from django.contrib import admin

from cart_and_orders.models import Order, OrderProduct


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "city",
        "address",
        "delivery_method",
        "status",
        "payment_method",
        "created_at"
    ]
    list_filter = ["status", "user"]
    search_fields = ["user", "city"]
    ordering = ["status", "user"]


@admin.register(OrderProduct)
class ProductSellerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "seller",
        "price",
        "quantity",
    )
