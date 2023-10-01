from django.db import models
from shopapp.models import ProductSeller, get_user_model


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
