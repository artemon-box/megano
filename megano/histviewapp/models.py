from django.conf import settings
from django.db import models
from shopapp.models import Product


class HistoryViewed(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-watched_at"]
        verbose_name = "История просмотра товаров"
        verbose_name_plural = "Истории просмотра товаров"

    def __str__(self):
        return f"{self.user} - {self.product} ({self.watched_at})"
