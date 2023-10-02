from django import forms


class OrderForm(forms.Form):
    DELIVERY_CHOICES = (
        ('ordinary', 'Обычная доставка'),
        ('express', 'Экспресс доставка'),
    )

    PAYMENT_CHOICES = (
        ('online', 'Онлайн картой'),
        ('someone', 'Онлайн со случайного чужого счета'),
    )

    name = forms.CharField(label='ФИО', max_length=255)
    phone = forms.CharField(label='Телефон', max_length=15)
    mail = forms.EmailField(label='E-mail')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=False)
    passwordReply = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput, required=False)

    delivery = forms.ChoiceField(label='Тип доставки',
                                 widget=forms.RadioSelect,
                                 choices=DELIVERY_CHOICES,
                                 required=True,
                                 )
    city = forms.CharField(label='Город', max_length=255)
    address = forms.CharField(label='Адрес', widget=forms.Textarea)

    payment = forms.ChoiceField(label='Способ оплаты',
                                widget=forms.RadioSelect,
                                choices=PAYMENT_CHOICES,
                                required=True,
                                )
