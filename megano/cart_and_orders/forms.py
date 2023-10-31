from cart_and_orders.models import DeliveryMethod
from config.settings import PAYMENT_CHOICES
from django import forms


class OrderForm(forms.Form):
    name = forms.CharField(label="ФИО", max_length=255)
    phone = forms.CharField(label="Телефон", max_length=19)
    mail = forms.EmailField(label="E-mail")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput, required=False)
    passwordReply = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput, required=False)
    city = forms.CharField(label="Город", max_length=255)
    address = forms.CharField(label="Адрес", widget=forms.Textarea)

    payment = forms.ChoiceField(
        label="Способ оплаты",
        widget=forms.RadioSelect,
        choices=PAYMENT_CHOICES,
        required=True,
    )

    delivery = forms.ModelChoiceField(
        label="Тип доставки",
        queryset=DeliveryMethod.objects.all(),  # Получите все доступные методы доставки
        widget=forms.RadioSelect,
        empty_label=None,  # Не отображайте пустой вариант выбора
        required=True,
    )
