from shopapp.models import Discount
from django.db.models import Q, Max
from django.utils import timezone as django_timezone
from decimal import Decimal


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
        result = {}
        products_in_cart = []
        categories_in_cart = []
        quantity_in_cart = 0

        for item in products:
            products_in_cart.append(item['product_seller'])
            categories_in_cart.append(item['product_seller'].product.category)
            quantity_in_cart += item['quantity']

        if isinstance(products[0], dict):
            total_price = sum(item["quantity"] * item["product_seller"].price for item in products)
        else:
            total_price = sum(item.quantity * item.product_seller.price for item in products)

        all_discounts = Discount.objects.filter(is_active=True).filter(
            Q(end__isnull=True) |
            Q(end__gte=django_timezone.now())).filter(
            Q(start__isnull=True) |
            Q(start__lte=django_timezone.now())
        ).prefetch_related('products', 'categories')

        all_cart_discounts = all_discounts.filter(type='c').filter(
            Q(cart_numbers__isnull=True) |
            Q(cart_numbers__lte=quantity_in_cart)).filter(
            # если в скидке указано мин кол-во товаров и оно меньше или равно кол-ву в корзине
            Q(cart_price__isnull=True) |
            Q(cart_price__lte=total_price)
        )
        result['cart_discounts'] = all_cart_discounts

        all_product_discounts = all_discounts.filter(type='p')
        all_set_discounts = all_discounts.filter(type='s')
        all_product_discounts = all_product_discounts.filter(
            products__in=products_in_cart) | all_product_discounts.filter(categories__name__in=categories_in_cart)
        result['product_discounts'] = all_product_discounts.distinct()  # только уникальные модели

        # выбираем скидки на наборы, если в корзине присутствуют товары, которые указаны в поле products и/или categories
        index = []
        for set_discount in all_set_discounts:
            if set_discount.products.all() and not set_discount.categories.all():
                products_match = all(products in set_discount.products.all() for products in products_in_cart)
                if products_match:
                    index.append(set_discount.id)
            if set_discount.categories.all() and not set_discount.products.all():
                categories_match = all(categories in set_discount.categories.all() for categories in categories_in_cart)
                if categories_match:
                    index.append(set_discount.id)
            if set_discount.products.all() and set_discount.categories.all():
                products_match = all(products in set_discount.products.all() for products in products_in_cart)
                categories_match = all(categories in set_discount.categories.all() for categories in categories_in_cart)
                if products_match and categories_match:
                    index.append(set_discount.id)
        all_set_discounts = all_set_discounts.filter(id__in=index)

        result["set_discounts"] = all_set_discounts
        result["total_price"] = total_price
        result['categories'] = categories_in_cart
        result['products'] = products_in_cart

        return result

    def get_priority_discount(self, products):
        """
        Получить приоритетную скидку на указанный список товаров или на один товар
        """
        data = self.get_all_discount_list_products_or_product(products)

        # если есть скидка на корзину, то берем наиболее приоритетную
        if data.get('cart_discounts'):
            qs = data.get('cart_discounts')
            highest_discounts = qs.filter(
                weight=qs.aggregate(max_weight=Max('weight'))['max_weight'])  # берем самые "тяжелые" скидки
            params = highest_discounts.aggregate(Max("percent"), Max("discount_volume"))
            if params["percent__max"] and not params["discount_volume__max"]:
                data['discount'] = qs.filter(percent=params["percent__max"])
            elif not params["percent__max"] and params["discount_volume__max"]:
                data['discount'] = qs.filter(discount_volume=params["discount_volume__max"])
            else:
                sum_discount = round(Decimal(params['percent__max'] / 100) * data['total_price'],
                                     2)  # сумма скидки рассчитанная
                if sum_discount >= params["discount_volume__max"]:
                    data['discount'] = qs.filter(percent=params["percent__max"])
                else:
                    data['discount'] = qs.filter(discount_volume=params["discount_volume__max"])
            return data

        # если корзинной скидки нет, начинаем искать скидку на набор
        if data.get("set_discounts"):
            qs = data.get("set_discounts")
            highest_discounts = qs.filter(
                weight=qs.aggregate(max_weight=Max('weight'))['max_weight'])  # берем самые "тяжелые" скидки

            discount_choice = {}
            # записываем в словарь скидки для фильтрации
            for discount in highest_discounts:
                if discount.get_volume:  # скидки у которых есть свойство get_volume
                    discount_choice[discount.get_volume] = discount.id
                if discount.discount_volume:  # скидки у которых нет get_volume, есть discount_volume
                    discount_choice[discount.discount_volume] = discount.id
                # считаем уровень скидкь если у нее указан процент и только категории
                if discount.categories.all() and discount.percent and not discount.products.all():
                    products_price = 0
                    for product in data.get('products'):
                        if product.product.category in discount.categories.all():  # если категория продукта попадает в категории скидки
                            products_price += product.price
                    discount_volume = round(Decimal(discount.percent / 100) * products_price, 2)
                    discount_choice[discount_volume] = discount.id

            max_key = max(discount_choice,
                          key=lambda key: Decimal(str(key)))  # находим максимум величины скидки в словаре
            data['discount'] = highest_discounts.filter(id=discount_choice[max_key])
            return data

        # если нет скидок на корзину и наборы, берём самые тяжелые скидки на продукты
        if data.get("product_discounts"):
            qs = data.get("product_discounts")
            highest_discounts = qs.filter(
                weight=qs.aggregate(max_weight=Max('weight'))['max_weight'])  # берем самые "тяжелые" скидки
            return highest_discounts
        return data

    def calculate_discount_price_product(self, products, base_price=None):
        """
        Рассчитать цену со скидкой на товар с дополнительным необязательным параметром Цена товара
        """

        data = self.get_priority_discount(products)
        total_price = data['total_price']

        # для скидок на корзину и наборы

        if len(data['discount']) == 1:
            discount = data['discount'][0]
            if discount.type == 'c':  # если на корзину
                if discount.percent:
                    price_with_discount = round(total_price * Decimal(discount.percent / 100), 2)
                else:
                    price_with_discount = total_price - discount.discount_volume
                if base_price and price_with_discount < base_price:
                    price_with_discount = base_price
                elif not base_price and price_with_discount < Decimal(1):
                    price_with_discount = Decimal(1)
                #print(total_price, price_with_discount)
                return price_with_discount, discount

            if discount.type == 's':  # если на набор
                set_price = 0
                for product_seller in data["products"]:
                    if product_seller.product in discount.products.all():
                        set_price += product_seller.price
                    if product_seller.product.category in discount.categories.all():
                        set_price += product_seller.price
                if discount.percent:
                    price_with_discount = total_price - round(set_price * Decimal(discount.percent / 100), 2)
                else:
                    price_with_discount = total_price - (set_price - discount.discount_volume)
                if base_price and price_with_discount < base_price:
                    price_with_discount = base_price
                elif not base_price and price_with_discount < Decimal(1):
                    price_with_discount = Decimal(1)
                #print(total_price, price_with_discount)
                return price_with_discount, discount
        else:
            pass
