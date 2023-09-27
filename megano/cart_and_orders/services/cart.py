from ..models import CartItems
from shopapp.models import ProductSeller


class CartService:
    def get_cart(self, user_id):
        """
        получение содержимого корзины для конкретного пользователя
        """
        cart_items = CartItems.objects.filter(user_id=user_id)

        return cart_items

    def add_to_cart(self, user_id, product_id, quantity=1):
        """
        добавление товара в корзину для конкретного пользователя
        """
        product_seller = ProductSeller.objects.get(pk=product_id)

        if product_seller:
            cart_item, created = CartItems.objects.get_or_create(
                user_id=user_id,
                product_seller=product_seller,
            )
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = 1
            cart_item.save()
            return cart_item.quantity

    def delete_from_cart(self, user_id, product_id):
        """
        удаление товара из корзины для конкретного пользователя
        """
        cart_item = CartItems.objects.get(user_id=user_id, product_seller=product_id)
        cart_item.delete()

    def change_count_of_product_in_cart(self, user_id, product_id, new_count):
        """
        изменение количества товара в корзине для конкретного пользователя
        """
        cart_item = CartItems.objects.get(user_id=user_id, product_seller=product_id)
        cart_item.quantity = new_count
        cart_item.save()
