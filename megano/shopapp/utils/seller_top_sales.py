from django.db.models import Sum, Case, When, Value, IntegerField, F

from cart_and_orders.models import Order, OrderProduct
from shopapp.models import ProductSeller, Product
from django.db.models import Sum, F
from django.db.models.functions import Coalesce


def seller_top_sales(seller):
    """
    Функция для подсчета и вывода количества продаж каждого товара для конкретного продавца

    """

    orders_products = OrderProduct.objects.filter(
        seller=seller,
        order__status='delivered'
    )

    product_quantities = orders_products.values('product', 'seller').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')

    top_products = []
    for item in product_quantities:
        product_id = item['product']
        total_quantity = item['total_quantity']
        seller = item['seller']

        product_seller = ProductSeller.objects.get(product_id=product_id, seller=seller)

        top_products.append({
            'seller_product': product_seller,
            'total_quantity': total_quantity,
        })

    return top_products


