from django.urls import path

from paymentapp.views import PaymentView

app_name = "paymentapp"

urlpatterns = [
    path('payment/', PaymentView.as_view(), name='payment'),
]
