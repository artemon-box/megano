from django import forms


class PaymentForm(forms.Form):

    number = forms.CharField(label='Номер карты')
