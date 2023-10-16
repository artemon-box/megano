from cart_and_orders.models import Order, OrderProduct
from shopapp.models import ProductSeller


def quantity_correction(order_id, increase=True):
    """
    Функция для списания количества товара у продавца при оформлении заказа.
    """

    product_orders = OrderProduct.objects.filter(order_id=order_id)
    for product_order in product_orders:
        product_seller = ProductSeller.objects.get(product=product_order.product, seller=product_order.seller)
        print(product_seller.quantity, '-', product_order.quantity)
        if increase:
            product_seller.quantity += product_order.quantity
        else:
            product_seller.quantity -= product_order.quantity
        product_seller.save()


