from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View


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
