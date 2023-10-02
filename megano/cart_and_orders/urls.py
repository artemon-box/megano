from django.urls import path

from cart_and_orders.views import OrderView

app_name = "cart_and_orders"

urlpatterns = [
    path('order/', OrderView.as_view(), name='order'),
]
