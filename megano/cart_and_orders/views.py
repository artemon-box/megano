from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from shopapp.forms import AddToCartForm

from .services.cart import CartService


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


class ClearCartView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        cart_service = CartService()
        cart_service.clear_cart(request)

        return redirect(request.META["HTTP_REFERER"])
