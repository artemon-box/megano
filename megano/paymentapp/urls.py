from django.urls import path
from paymentapp.views import PaymentView, PaymentSomeoneView

app_name = "paymentapp"

urlpatterns = [
    path('payment/', PaymentView.as_view(), name='payment'),
    path('payment_someone/', PaymentSomeoneView.as_view(), name='payment_someone'),
]
