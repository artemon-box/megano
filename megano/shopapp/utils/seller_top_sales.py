import random

from cart_and_orders.models import Order, OrderProduct
from django.db.models import Case, F, IntegerField, Sum, Value, When
from django.db.models.functions import Coalesce
from shopapp.models import Product, ProductSeller


def seller_top_sales(seller):
    """
    Функция для подсчета и вывода количества продаж каждого товара для конкретного продавца

    """

    orders_products = OrderProduct.objects.filter(seller=seller, order__status="delivered")

    product_quantities = (
        orders_products.values("product", "seller")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")
    )

    top_products = []
    for item in product_quantities:
        product_id = item["product"]
        total_quantity = item["total_quantity"]
        seller = item["seller"]

        product_seller = ProductSeller.objects.get(product_id=product_id, seller=seller)

        top_products.append(
            {
                "seller_product": product_seller,
                "total_quantity": total_quantity,
            }
        )

    if not top_products:
        product_sellers = list(ProductSeller.objects.filter(seller=seller)[:10])
        random.shuffle(product_sellers)

        for product_seller in product_sellers:
            top_products.append(
                {
                    "seller_product": product_seller,
                    "total_quantity": 0,
                }
            )

    return top_products
