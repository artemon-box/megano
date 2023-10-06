from cart_and_orders.models import Order
import requests
from paymentapp.tasks import process_payment


class PaymentService:
    @staticmethod
    def initiate_payment(order_id, card_number, price):
        """
        Метод для инициирования оплаты заказа.

        :param order_id: ID заказа, который нужно оплатить.
        :param card_number: Номер кредитной карты для оплаты.
        :param price: Сумма к оплате.
        :return: Успешность и информация о запросе на оплату.
        """

        payment_task = process_payment.apply_async(args=(order_id, card_number, price))

        return {
            "success": True,
            "message": "Запрос на оплату успешно отправлен.",
            "task_id": payment_task.id,
        }

    @staticmethod
    def get_payment_status(task_id):
        """
        Метод для получения статуса оплаты заказа.

        :param task_id: ID задачи оплаты из Celery.
        :return: Статус оплаты и информация о заказе.
        """
        try:
            task_result = process_payment.AsyncResult(task_id)
            if task_result.state == "SUCCESS":
                order_id, payment_status, price = task_result.result
                order = Order.objects.get(id=order_id)
                return {
                    "success": True,
                    "message": f"Статус оплаты заказа {order.id}: {payment_status}",
                }
            else:
                return {
                    "success": False,
                    "message": "Запрос на оплату еще не завершен.",
                }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
            }
