from django.contrib.auth import get_user_model
from django.db import models

from shopapp.models import Product


class OrderItem(models.Model):
    product = models.ManyToManyField(Product)
    order_quantity = models.IntegerField(verbose_name='количество', default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='цена товара у продавца')


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    order_items = models.ForeignKey(OrderItem, on_delete=models.RESTRICT)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    fio = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, default=None)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=12)
    city = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    delivery_method = models.CharField(max_length=100, default=None)
    payment_method = models.CharField(max_length=100, default=None)

    class Meta:
        ordering = ['-created_at',]
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]


