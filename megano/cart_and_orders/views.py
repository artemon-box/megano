import re

from accountapp.accounts import cmd_create_buyer
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from shopapp.forms import AddToCartForm

from .forms import OrderForm
from .models import DeliveryMethod, Order, OrderProduct
from .services.cart import CartService
from .utils.get_total_price import get_total_price_delivery, get_total_price


class CartView(View):
    template_name = "cart_and_orders/cart.jinja2"

    def get(self, request: HttpRequest) -> HttpResponse:
        cart_service = CartService()

        cart_items = cart_service.get_cart(request)

        context = {
            "cart_items": cart_items,
        }

        return render(request, self.template_name, context=context)


class AddToCartView(View):
    def get(self, request: HttpRequest, product_id, quantity=1) -> HttpResponse:
        cart_service = CartService()

        cart_service.add_to_cart(request, product_id, quantity)

        return redirect(request.META["HTTP_REFERER"])


class RemoveFromCartView(View):
    def get(self, request: HttpRequest, product_id) -> HttpResponse:
        cart_service = CartService()
        cart_service.delete_from_cart(request, product_id)

        return redirect(request.META["HTTP_REFERER"])


class ChangeCountInCartView(View):
    def post(self, request, product_id):
        form = AddToCartForm(request.POST)
        if form.is_valid():
            new_count = form.cleaned_data["order_quantity"]
            cart_service = CartService()
            cart_service.change_count_of_product_in_cart(request, product_id, new_count)
            return redirect(request.META["HTTP_REFERER"])


class OrderView(View):
    """
    Представление для отображения страницы оформления заказа.
    """

    cart = CartService()

    @classmethod
    def get_phone(cls, phone):
        """
        Метод получения чистого номера телефона
        """

        return re.sub(r"\D", "", phone)[1:]

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик GET-запроса для отображения информации о заказе.

        :param request: Запрос пользователя.
        :return: HTTP-ответ с детальной информацией о заказе.
        """

        product_seller = self.cart.get_cart(request)

        user_orders = Order.objects.filter(user_id=request.user, status="created")
        if user_orders:
            user_orders.delete()

        if not product_seller:
            raise Http404("Корзина пуста")

        first_delivery_method = DeliveryMethod.objects.first()
        order_form = OrderForm(initial={"delivery": first_delivery_method, "payment": "online"})
        context = {
            "form": order_form,
        }
        return render(request, "cart_and_orders/order.jinja2", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик POST-запросов для отображения детальной информации о заказе.

        :param request: Запрос пользователя.
        :return: HTTP-ответ с детальной информацией о заказе.
        """
        order_form = OrderForm(request.POST)
        cart = self.cart.get_cart(request)
        user = request.user

        if order_form.is_valid():
            if not request.user.is_authenticated:
                user = cmd_create_buyer(
                    name=order_form.cleaned_data["name"],
                    email=order_form.cleaned_data["mail"],
                    password=order_form.cleaned_data["password"],
                )
                user.phone = self.get_phone(order_form.cleaned_data["phone"])
                user.save()

            request.user.phone = self.get_phone(order_form.cleaned_data["phone"])
            request.user.save()

            order = Order.objects.create(
                user=user,
                city=order_form.cleaned_data["city"],
                address=order_form.cleaned_data["address"],
                delivery_method=order_form.cleaned_data["delivery"],
                payment_method=order_form.cleaned_data["payment"],
            )

            order.save()

            for item in cart:
                product_seller = item["product_seller"]
                quantity = item["quantity"]

                order_item = OrderProduct.objects.create(
                    order=order,
                    product=product_seller.product,
                    seller=product_seller.seller,
                    quantity=quantity,
                    price=product_seller.price,
                )

                order_item.save()

            order.total_price = get_total_price_delivery(order.id)
            order.save()

            request.session["current_order_id"] = order.id

            return redirect("cart_and_orders:order_confirm")

        else:
            context = {
                "form": order_form,
            }
            return render(request, "cart_and_orders/order.jinja2", context)


class OrderConfirmView(View):
    """
    Представление для отображения страницы подтверждения заказа.
    """

    cart = CartService()

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Обработчик GET-запроса для отображения информации о заказе.

        :param request: Запрос пользователя.
        :return: HTTP-ответ с детальной информацией о заказе.
        """
        current_order_id = request.session.get("current_order_id")
        order = Order.objects.get(id=current_order_id)
        total_price = get_total_price_delivery(current_order_id)
        full_price = get_total_price(current_order_id)
        product_seller = self.cart.get_cart(request)

        context = {
            "order": order,
            "order_price": total_price,
            'full_price': full_price,
            "cart": product_seller,
        }

        return render(request, "cart_and_orders/order_confirm.jinja2", context)


class ClearCartView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        cart_service = CartService()
        cart_service.clear_cart(request)

        return redirect(request.META["HTTP_REFERER"])
