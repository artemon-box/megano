class CartService:
    def get_cart(self, user_id):
        """
        получение содержимого корзины для конкретного пользователя
        """
        pass

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
