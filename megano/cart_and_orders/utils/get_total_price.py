from cart_and_orders.models import Order, OrderProduct
from shopapp.models import ProductSeller


def get_total_price(order_id):
    """
    Метод получения полной стоимости заказа
    """

    items = OrderProduct.objects.filter(order_id=order_id)
    total_price = 0
    for item in items:
        total_price += item.quantity * ProductSeller.objects.get(seller=item.seller, product=item.product).price

    return total_price


def get_total_price_with_discount(order_id):
    """
    Метод получения полной стоимости заказа с учетом скидок
    """

    items = OrderProduct.objects.filter(order_id=order_id)
    total_price = 0
    for item in items:
        total_price += item.quantity * item.price

    return total_price


def get_total_delivery_price(order_id):
    """
    Метод получения полной стоимости заказа с учётом доставки
    """

    total_price = get_total_price(order_id)
    delivery = Order.objects.get(id=order_id).delivery_method
    unique_sellers_count = OrderProduct.objects.filter(order__id=order_id).values("seller").distinct().count()

    if delivery.order_minimal_price is None:
        return delivery.price
    elif total_price < delivery.order_minimal_price or unique_sellers_count > 1:
        return delivery.price
    else:
        return 0
