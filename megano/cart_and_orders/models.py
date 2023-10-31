from django.contrib.auth import get_user_model
from django.db import models
from shopapp.models import Product, ProductSeller, Seller


class CartItems(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product_seller = models.ForeignKey(ProductSeller, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return (
            f"Корзина {self.user.name} |"
            f" Продукты {self.product_seller.product.name} | "
            f"Количество товаров {self.quantity}"
        )


class DeliveryMethod(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название метода доставки")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена доставки")
    order_minimal_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена заказа для расчёта стоимости доставки",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class StatusOrder(models.TextChoices):
    CREATED = "created", "Cоздан"
    PENDING = "pending", "Ожидает оплаты"
    PAID = "paid", "Оплачен"
    FAILED = "failed", "Ошибка оплаты"
    PROCESSING = "processing", "Обрабатывается"
    SHIPPED = "shipped", "Отправлен"
    DELIVERED = "delivered", "Доставлен"
    CANCELED = "canceled", "Отменен"

    @classmethod
    def get_main_status(cls):
        """
        Список для показа основных заказов в кабинете пользователя
        """
        return [
            cls.CREATED.value,
            cls.PENDING.value,
            cls.PAID.value,
            cls.FAILED.value,
            cls.PROCESSING.value,
            cls.SHIPPED.value,
        ]


class Order(models.Model):
    """
    Таблица для хранения данных о заказах.

    """

    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    city = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    delivery_method = models.ForeignKey(
        DeliveryMethod, on_delete=models.CASCADE, null=True, verbose_name="Метод доставки"
    )
    payment_method = models.CharField(max_length=100, default=None)
    total_price = models.DecimalField(
        max_digits=100,
        decimal_places=2,
        verbose_name="полная цена заказа",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=StatusOrder.choices,
        default=StatusOrder.CREATED,
    )

    class Meta:
        ordering = ["-status"]

    def __str__(self):
        return f"{self.user}'s order #{self.pk} status: {self.status}"


class OrderProduct(models.Model):
    """
    Промежуточная таблица для хранения данных о товаре, количестве в конкретном заказе.

    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    seller = models.ForeignKey(Seller, on_delete=models.RESTRICT)
    quantity = models.IntegerField(verbose_name="количество", default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="цена товара у продавца")

    class Meta:
        verbose_name = "товар в заказе"
        verbose_name_plural = "товары в заказах"
        unique_together = (
            "order",
            "product",
            "seller",
        )

    def __str__(self):
        return f"{self.product} in {self.order} by {self.seller}"
