from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect
from django.views import View
from .forms import OrderForm
from .services.cart import CartService


class OrderView(View):
    """
    Представление для отображения страницы оформления заказа.
    """

    cart = CartService()

    def get_total_price(self, cart):
        """
        Метод получения полной стоимости заказа
        """

        total_price = 0

        for item in cart:
            total_price += item['product_seller'].price

        return total_price

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик GET-запроса для отображения информации о заказе.

        :param request: Запрос пользователя.
        :return: HTTP-ответ с детальной информацией о заказе.
        """

        product_seller = self.cart.get_cart(request)
        total_price = self.get_total_price(product_seller)

        order_form = OrderForm(initial={'delivery': 'ordinary', 'payment': 'online'})
        context = {
            'form': order_form,
            'cart': product_seller,
            'total_price': total_price,
        }
        return render(request, 'cart_and_orders/order.jinja2', context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик POST-запросов для отображения детальной информации о продукте.

        :param request: Запрос пользователя.
        :return: HTTP-ответ с детальной информацией о товаре.
        """
        order_form = OrderForm(request.POST)

        print(request.POST)

        if order_form.is_valid():
            return redirect('paymentapp:payment')
        else:

            print(type(order_form.errors))

            product_seller = self.cart.get_cart(request)
            total_price = self.get_total_price(product_seller)

            context = {
                'form': order_form,
                'cart': product_seller,
                'total_price': total_price,
            }
            return render(request, 'cart_and_orders/order.jinja2', context)


