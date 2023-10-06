from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from cart_and_orders.models import Order
from .forms import PaymentForm
from .services.payment import PaymentService


class PaymentView(View):
    """
    Представление для отображения страницы оформления заказа.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик GET-запроса для оплаты заказа.

        :param request: Запрос пользователя.
        :return: HTTP-ответ со страницей оплаты.
        """

        return render(request, 'paymentapp/payment.jinja2')

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик POST-запросов для оплаты заказа.

        :param request: Запрос пользователя.
        :return: HTTP-ответ с детальной информацией об оплате.
        """
        print(request.POST)

        payment_service = PaymentService()

        current_order_id = request.session.get('current_order_id')
        if current_order_id:
            order = Order.objects.get(id=current_order_id)
            total_price = order.total_price
        else:
            raise ValueError('Ошибка заказа')

        card_number = request.POST['number'].replace(" ", "")

        response = payment_service.initiate_payment(order.id, card_number, total_price)

        return redirect('shopapp:index')

