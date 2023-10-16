from django.http import HttpRequest, HttpResponse, Http404, JsonResponse
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
        if request.session.get('current_order_id'):
            current_order_id = request.session.get('current_order_id')
            order = Order.objects.get(id=current_order_id)
            if order.status != 'created':
                raise Http404("Запрошенный заказ в обработке")
        else:
            raise Http404("Запрошенный заказ не найден")

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
            raise ValueError('Заказ в обработке')

        card_number = request.POST['number'].replace(" ", "")

        # payment_service.initiate_payment(order.id, card_number, total_price)

        del request.session['current_order_id']

        return redirect('paymentapp:progress_payment')


class PaymentSomeoneView(View):
    """
    Представление для отображения страницы оформления заказа.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик GET-запроса для оплаты заказа.

        :param request: Запрос пользователя.
        :return: HTTP-ответ со страницей оплаты.
        """
        if request.session.get('current_order_id'):
            current_order_id = request.session.get('current_order_id')
            order = Order.objects.get(id=current_order_id)
            if order.status != 'created':
                raise Http404("Запрошенный заказ в обработке")
        else:
            raise Http404("Запрошенный заказ не найден")

        return render(request, 'paymentapp/payment_someone.jinja2')

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик POST-запросов для оплаты заказа.

        :param request: Запрос пользователя.
        :return: HTTP-ответ с детальной информацией об оплате.
        """

        payment_service = PaymentService()

        current_order_id = request.session.get('current_order_id')
        if current_order_id:
            order = Order.objects.get(id=current_order_id)
            total_price = order.total_price
        else:
            raise ValueError('Заказ в обработке')

        card_number = request.POST['number'].replace(" ", "")

        response = payment_service.initiate_payment(order.id, card_number, total_price)
        request.session['task_id'] = response['task_id']

        del request.session['current_order_id']

        return redirect('paymentapp:progress_payment')


class ProgressPaymentView(View):
    """
    Представление для отображения страницы оформления заказа.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик GET-запроса для ожидания подтверждения оплаты заказа.

        :param request: Запрос пользователя.
        :return: HTTP-ответ со страницей ожидания подтверждения оплаты.
        """

        return render(request, 'paymentapp/progress_payment.jinja2')


class CheckPaymentStatusView(View):
    def get(self, request):

        payment_service = PaymentService()
        task_id = request.session.get('task_id')

        status = payment_service.get_payment_status(task_id)['status']

        return JsonResponse({'status': status})
