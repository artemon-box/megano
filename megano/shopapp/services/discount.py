class DiscountService:
    def get_discounts_from_shop(self, user_id, shop_id):
        """
        получение списка всех скидок в магазине с учетом профиля пользователя
        """
        pass

    def get_category_discounts_from_shop(self, user_id, shop_id, category_id):
        """
        получение списка скидок из определенной категории магазина с учетом профиля пользователя
        """
        pass

    def get_discounts_from_mall(self, user_id):
        """
        получение списка скидок всех товаров торгового центра с учетом профиля пользователя
        """
        pass

    def get_category_discounts_from_mall(self, user_id, category_id):
        """
        получения списка скидок из определенной категории товаров во всем торговом центре с учетом профиля пользователя
        """
        pass

    def get_all_discount_list_products_or_product(self, products):
        """
        Получить все скидки на указанный список товаров или на один товар
        """

    def get_priority_discount(self, products):
        """
        Получить приоритетную скидку на указанный список товаров или на один товар
        """

    def calculate_discount_price_product(self, product, base_price=None):
        """
        Рассчитать цену со скидкой на товар с дополнительным необязательным параметром Цена товара
        """
