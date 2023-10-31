from cart_and_orders.models import Order
from cart_and_orders.services.cart import CartService
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View

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
        if request.session.get("current_order_id"):
            current_order_id = request.session.get("current_order_id")
            order = Order.objects.get(id=current_order_id)
            if order.status not in ("created", "failed"):
                raise Http404("Запрошенный заказ в обработке", order.status)
        else:
            raise Http404("Запрошенный заказ не найден")

        return render(request, "paymentapp/payment.jinja2")

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик POST-запросов для оплаты заказа.

        :param request: Запрос пользователя.
        :return: HTTP-ответ с детальной информацией об оплате.
        """

        payment_service = PaymentService()
        cart = CartService()

        cart.clear_cart(request)

        current_order_id = request.session.get("current_order_id")
        if current_order_id:
            order = Order.objects.get(id=current_order_id)
            total_price = order.total_price
            order.status = "pending"
            order.save()
        else:
            raise ValueError("Заказ в обработке")

        card_number = request.POST["number"].replace(" ", "")

        response = payment_service.initiate_payment(order.id, card_number, total_price)
        request.session["task_id"] = response.get("task_id")

        return redirect("paymentapp:progress_payment")


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
        if request.session.get("current_order_id"):
            current_order_id = request.session.get("current_order_id")
            order = Order.objects.get(id=current_order_id)
            if order.status != "created":
                raise Http404("Запрошенный заказ в обработке")
        else:
            raise Http404("Запрошенный заказ не найден")

        return render(request, "paymentapp/payment_someone.jinja2")

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик POST-запросов для оплаты заказа.

        :param request: Запрос пользователя.
        :return: HTTP-ответ с детальной информацией об оплате.
        """

        payment_service = PaymentService()
        cart = CartService()

        cart.clear_cart(request)

        current_order_id = request.session.get("current_order_id")
        if current_order_id:
            order = Order.objects.get(id=current_order_id)
            total_price = order.total_price
            order.status = "pending"
            order.save()
        else:
            raise ValueError("Заказ в обработке")

        card_number = request.POST["number"].replace(" ", "")

        response = payment_service.initiate_payment(order.id, card_number, total_price)
        request.session["task_id"] = response.get("task_id")

        return redirect("paymentapp:progress_payment")


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

        task_id = request.session.get("task_id")
        order_id = request.session.get("current_order_id")

        del request.session["current_order_id"]

        context = {
            "task_id": task_id,
            "order_id": order_id,
        }

        return render(request, "paymentapp/progress_payment.jinja2", context=context)


class CheckPaymentStatusView(View):
    """
    Представление для получения статуса оплаты заказа.
    """

    def get(self, request):
        """
        Обработчик GET-запроса для получения статуса оплаты заказа.

        :param request: Запрос пользователя.
        :return: JSON-ответ со статусом оплаты заказа.
        """

        payment_service = PaymentService()

        task_id = request.GET.get("task_id")

        status = payment_service.get_payment_status(task_id)["status"]

        return JsonResponse({"status": status})
