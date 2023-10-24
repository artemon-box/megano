import requests
from cart_and_orders.models import Order
from paymentapp.tasks import process_payment
from paymentapp.utils.quantity_correction import quantity_correction


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

        quantity_correction(order_id, increase=False)

        try:
            payment_task = process_payment.apply_async(args=(order_id, card_number, price))
            success = True
        except ConnectionRefusedError:
            success = False

        return {
            "success": success,
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

        if not task_id:
            raise ValueError("Идентификатор задачи отсутствует")

        result = process_payment.AsyncResult(task_id)
        if result.state == "SUCCESS":
            return {"status": "success"}
        elif result.state == "FAILURE":
            return {"status": "failed"}
        else:
            return {"status": "pending"}
