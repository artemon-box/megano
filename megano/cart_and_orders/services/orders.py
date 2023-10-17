from cart_and_orders.models import Order


class CompletedOrdersService:
    @classmethod
    def get_orders(cls, user):
        """
        Получение списка совершенных заказов для конкретного пользователя
        """

        orders = Order.objects.get(user=user).filter(status="delivered")

        return orders
