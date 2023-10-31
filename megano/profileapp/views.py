import os
import re

from cart_and_orders.models import Order, OrderProduct, ProductSeller, StatusOrder
from cart_and_orders.utils.get_total_price import get_total_delivery_price
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import ProfileAvatarForm, ProfileForm


class AccountView(View):
    template_name = "profileapp/account.jinja2"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("/")
        user = request.user
        status_view = StatusOrder.get_main_status()
        orders = Order.objects.filter(user=user, status__in=status_view)

        context = {
            "user": user,
            "orders": orders,
            "DELIVERY_CHOICES": settings.DELIVERY_CHOICES,
            "PAYMENT_CHOICES": settings.PAYMENT_CHOICES,
            "ORDER_STATUS_CHOICES": StatusOrder.choices,
        }
        return render(request, self.template_name, context)


class HistoryOrdersView(View):
    template_name_id = "profileapp/historyorder_id.jinja2"
    template_name = "profileapp/historyorder.jinja2"

    def get(self, request, *args, order_id=None, **kwargs):
        if not request.user.is_authenticated:
            return redirect("/")
        if order_id:
            user_order = Order.objects.filter(user=request.user, pk=order_id).exists()
            if not user_order:
                raise Http404("Запрошенный заказ не найден")
            request.session["current_order_id"] = order_id
            current_order_id = request.session.get("current_order_id")
            order = Order.objects.get(id=current_order_id)
            order_products = OrderProduct.objects.filter(order_id=order.id)

            context = {
                "order": order,
                "order_products": order_products,
                "STATUS_ORDER": StatusOrder,
                "PAYMENT_CHOICES": settings.PAYMENT_CHOICES,
            }
            return render(request, self.template_name_id, context)
        else:
            user = request.user
            orders = Order.objects.filter(user=user)

            context = {
                "user": user,
                "orders": orders,
                "DELIVERY_CHOICES": settings.DELIVERY_CHOICES,
                "PAYMENT_CHOICES": settings.PAYMENT_CHOICES,
                "ORDER_STATUS_CHOICES": StatusOrder.choices,
            }
            return render(request, self.template_name, context)


class ProfileView(View):
    template_name = "profileapp/profile.jinja2"
    form_class = ProfileForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("/")
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {"form": form, "user": request.user, "saved": False})

    def post(self, request):
        form = self.form_class(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            if password:
                user.set_password(password)
                user.save()
                user = authenticate(username=email, password=password)
                if user is not None:
                    login(request, user)
        else:
            # Форма не прошла валидацию, возвращаем с ошибками
            return render(request, self.template_name, {"form": form, "user": request.user, "saved": False})
        return render(request, self.template_name, {"form": form, "user": request.user, "saved": True})


class ProfileAvatarView(APIView):
    form_class = ProfileAvatarForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = request.user

            # Удаляем старый аватар, если он есть
            if user.avatar:
                old_avatar_path = os.path.join(settings.MEDIA_ROOT, str(user.avatar))
                if os.path.isfile(old_avatar_path):
                    os.remove(old_avatar_path)

            # Генерируем новое имя файла
            email = user.email
            filename = re.sub(r"[@.]", "_", email) + "_avatar" + os.path.splitext(request.FILES["avatar"].name)[-1]

            # Сохраняем новый аватар
            user.avatar.save(filename, request.FILES["avatar"])
            user.save()
            return Response({"message": "Avatar successfully updated"}, status=200)
        error_message = "Произошла ошибка при загрузке аватара. Пожалуйста, попробуйте еще раз."
        if "avatar" in form.errors:
            error_message = form.errors["avatar"][0]
        return Response({"message": error_message}, status=400)
