from shopapp.models import ProductSeller

from ..models import CartItems


class CartService:
    def get_cart(self, request):
        """
        Получение содержимого корзины для текущего пользователя
        """
        user = request.user
        cart_items = []

        if user.is_authenticated:
            # Если пользователь авторизован, получение его корзины из базы данных
            cart_items_db = CartItems.objects.filter(user=user)

            for item in cart_items_db:
                cart_items.append(
                    {
                        "product_seller": item.product_seller,
                        "quantity": item.quantity,
                    }
                )
        else:
            # Если не авторизован, то получение его корзины из сессии
            cart = request.session.get("cart", {})
            for product_id, quantity in cart.items():
                product_seller = ProductSeller.objects.get(pk=product_id)
                cart_items.append(
                    {
                        "product_seller": product_seller,
                        "quantity": quantity,
                    }
                )

        return cart_items

    def add_to_cart(self, request, product_id, quantity=1):
        """
        Добавление товара в корзину текущего пользователя
        """
        user = request.user

        if user.is_authenticated:
            # Если пользователь авторизован, товар добавляется в базу данных
            product_seller = ProductSeller.objects.get(pk=product_id)
            cart_item, created = CartItems.objects.get_or_create(
                user=user,
                product_seller=product_seller,
            )
            if not created:
                cart_item.quantity += int(quantity)
            else:
                cart_item.quantity = int(quantity)
            cart_item.save()
        else:
            # Если пользователь неавторизован, то товар добавляется в сессию
            cart = request.session.get("cart", {})
            cart_item = cart.get(str(product_id), 0)
            cart[product_id] = cart_item + int(quantity)
            request.session["cart"] = cart

    def delete_from_cart(self, request, product_id):
        """
        Удаление товара из корзины текущего пользователя
        """
        user = request.user

        if user.is_authenticated:
            # Если пользователь авторизован, товар удаляется из БД
            CartItems.objects.filter(user=user, product_seller_id=product_id).delete()
        else:
            # Если не авторизован, то из сессии
            cart = request.session.get("cart", {})
            if str(product_id) in cart:
                del cart[str(product_id)]
                request.session["cart"] = cart

    def change_count_of_product_in_cart(self, request, product_id, new_count):
        """
        Изменение количества товара в корзине текущего пользователя
        """
        user = request.user

        if user.is_authenticated:
            cart_item = CartItems.objects.get(user=user, product_seller_id=product_id)
            cart_item.quantity = new_count
            cart_item.save()

        else:
            cart = request.session.get("cart", {})
            cart[product_id] = new_count
            request.session["cart"] = cart

    def merge_carts(self, request, user):
        # Получение корзины из сессии
        session_cart = request.session.get("cart", {})

        # Получение корзины из БД
        cart_items_db = CartItems.objects.filter(user=user)
        db_cart = {str(item.product_seller.id): item.quantity for item in cart_items_db}

        # Объединение корзин
        for product_id, quantity in session_cart.items():
            db_quantity = db_cart.get(product_id, 0)
            db_cart[product_id] = db_quantity + quantity

        # Сохранение объединенной корзины в БД
        for product_id, quantity in db_cart.items():
            product_seller = ProductSeller.objects.get(pk=product_id)
            cart_item, created = CartItems.objects.get_or_create(
                user=user,
                product_seller=product_seller,
            )
            cart_item.quantity = quantity
            cart_item.save()

        request.session["cart"] = {}
