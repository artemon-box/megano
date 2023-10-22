import json

import requests
from cart_and_orders.models import Order
from config.celery import app


@app.task
def process_payment(order_id, card_number, price):
    """
    Задача Celery для обработки оплаты заказа.

    :param order_id: ID заказа, который нужно оплатить.
    :param card_number: Номер кредитной карты для оплаты.
    :param price: Сумма к оплате.
    :return: Информация о заказе и статус оплаты.
    """

    try:
        url = "http://payment_app:5000/pay"

        data = {"order_number": order_id, "card_number": card_number, "price": str(price)}

        response = requests.post(url, json=data)
        result = response.json()

        order = Order.objects.get(id=order_id)
        if result["status"] == "success":
            order.status = "paid"
        else:
            order.status = "failed"
        order.save()

        return order_id, result["status"], price

    except Exception as e:
        raise Exception(str(e))
