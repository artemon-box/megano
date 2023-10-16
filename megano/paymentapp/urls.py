from django.urls import path
from .views import PaymentView, PaymentSomeoneView, ProgressPaymentView, CheckPaymentStatusView

app_name = "paymentapp"

urlpatterns = [
    path('payment/', PaymentView.as_view(), name='payment'),
    path('payment_someone/', PaymentSomeoneView.as_view(), name='payment_someone'),
    path('progress_payment/', ProgressPaymentView.as_view(), name='progress_payment'),
    path('check_status/', CheckPaymentStatusView.as_view(), name='check_payment_status'),
]
