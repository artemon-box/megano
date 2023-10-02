from shopapp.models import ProductSeller


class CartService:
    def get_cart(self, request):
        """
        Получение содержимого корзины для текущего пользователя
        """
        user = request.user
        cart = request.session.get('cart', {})
        cart_items = []

        # if user.is_authenticated:
        #     cart_items_db = CartItems.objects.filter(user=user)
        #
        #     cart = {str(item.product_seller.id): item.quantity for item in cart_items_db}
        #     request.session['cart'] = cart
        #
        # for product_id, quantity in cart.items():
        for i in range(1, 4):
            product_seller = ProductSeller.objects.get(pk=i)
            cart_items.append({
                'product_seller': product_seller,
                'quantity': 10,
            })

        return cart_items

    def add_to_cart(self, user_id, product_slug, quantity):
        """
        добавление товара в корзину для конкретного пользователя
        """
        pass

    def delete_from_cart(self, user_id, product_id):
        """
        удаление товара из корзины для конкретного пользователя
        """
        pass

    def change_count_of_product_in_cart(self, user_id, product_id, new_count):
        """
        изменение количества товара в корзине для конкретного пользователя
        """
        pass
