from cart_and_orders.models import Order


class CompletedOrdersService:
    def get_orders(self, user):
        """
        получение списка совершенных заказов для конкретного пользователя
        """

        orders = Order.objects.get(user=user).filter(status='delivered')

        return orders