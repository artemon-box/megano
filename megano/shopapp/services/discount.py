from decimal import Decimal
from django.db.models import Max, Q
from django.utils import timezone as django_timezone
from shopapp.models import Discount


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

    def get_all_discount_list_products_or_product(self, products, total_price):
        """
        Получить все скидки на указанный список товаров или на один товар
        """
        result = {}
        products_in_cart = []
        categories_in_cart = []
        quantity_in_cart = 0
        products_with_quantity = []

        if products:
            for item in products:
                products_in_cart.append(item["product_seller"])
                categories_in_cart.append(item["product_seller"].product.category)
                quantity_in_cart += item["quantity"]
                products_with_quantity.append([item["product_seller"], item["quantity"]])

        all_discounts = (
            Discount.objects.filter(is_active=True)
            .filter(Q(end__isnull=True) | Q(end__gte=django_timezone.now()))
            .filter(Q(start__isnull=True) | Q(start__lte=django_timezone.now()))
            .prefetch_related("products", "categories")
        )

        all_cart_discounts = (
            all_discounts.filter(type="c")
            .filter(Q(cart_numbers__isnull=True) | Q(cart_numbers__lte=quantity_in_cart))
            .filter(
                # если в скидке указано мин кол-во товаров и оно меньше или равно кол-ву в корзине
                Q(cart_price__isnull=True)
                | Q(cart_price__lte=total_price)
            )
        )
        result["cart_discounts"] = all_cart_discounts

        all_product_discounts = all_discounts.filter(type="p")
        all_set_discounts = all_discounts.filter(type="s")
        all_product_discounts = all_product_discounts.filter(
            products__in=products_in_cart
        ) | all_product_discounts.filter(categories__name__in=categories_in_cart)
        result["product_discounts"] = all_product_discounts.distinct()  # только уникальные модели

        # выбираем скидки на наборы, если в корзине присутствуют товары, которые указаны в поле products и/или categories
        index = []
        for set_discount in all_set_discounts:
            if set_discount.products.all() and not set_discount.categories.all():
                products_match = all(products in products_in_cart for products in set_discount.products.all())
                if products_match:
                    index.append(set_discount.id)
            if set_discount.categories.all() and not set_discount.products.all():
                categories_match = all(
                    categories in categories_in_cart for categories in set_discount.categories.all()
                )
                if categories_match:
                    index.append(set_discount.id)
            if set_discount.products.all() and set_discount.categories.all():
                products_match = all(products in products_in_cart for products in set_discount.products.all())
                categories_match = all(
                    categories in categories_in_cart for categories in set_discount.categories.all()
                )
                if products_match and categories_match:
                    index.append(set_discount.id)
        all_set_discounts = all_set_discounts.filter(id__in=index)

        result["set_discounts"] = all_set_discounts
        result["categories"] = categories_in_cart
        result["products"] = products_in_cart
        result["products_pcs"] = products_with_quantity

        return result

    def get_priority_discount(self, products, total_price):
        """
        Получить приоритетную скидку на указанный список товаров или на один товар
        """
        data = self.get_all_discount_list_products_or_product(products, total_price)

        # если есть скидка на корзину, то берем наиболее приоритетную
        if data.get("cart_discounts"):
            qs = data.get("cart_discounts")
            highest_discounts = qs.filter(
                weight=qs.aggregate(max_weight=Max("weight"))["max_weight"]
            )  # берем самые "тяжелые" скидки
            params = highest_discounts.aggregate(Max("percent"), Max("discount_volume"))
            if params["percent__max"] and not params["discount_volume__max"]:
                data["discount"] = qs.filter(percent=params["percent__max"])
            elif not params["percent__max"] and params["discount_volume__max"]:
                data["discount"] = qs.filter(discount_volume=params["discount_volume__max"])
            else:
                sum_discount = round(
                    Decimal(params["percent__max"] / 100) * total_price, 2
                )  # сумма скидки рассчитанная
                if sum_discount >= params["discount_volume__max"]:
                    data["discount"] = qs.filter(percent=params["percent__max"])
                else:
                    data["discount"] = qs.filter(discount_volume=params["discount_volume__max"])
            return data

        # если корзинной скидки нет, начинаем искать скидку на набор
        if data.get("set_discounts"):
            qs = data.get("set_discounts")
            highest_discounts = qs.filter(
                weight=qs.aggregate(max_weight=Max("weight"))["max_weight"]
            )  # берем самые "тяжелые" скидки
            discount_choice = {}
            # записываем в словарь скидки для фильтрации
            for discount in highest_discounts:
                if discount.discount_volume:  # скидки у которых нет get_volume, есть discount_volume
                    discount_choice[discount.discount_volume] = discount.id
                # считаем уровень скидки если у нее указан процент и только категории
                elif discount.percent:
                    products_price = 0
                    for product in data.get("products"):
                        if (
                                product.product.category in discount.categories.all() or product in discount.products.all()
                        ):  # если категория продукта попадает в категории скидки
                            products_price += product.price
                    discount_volume = round(Decimal(discount.percent / 100) * Decimal(products_price),
                                            2)  # Decimal(p_p)
                    discount_choice[discount_volume] = discount.id
            max_key = max(
                discount_choice, key=lambda key: Decimal(str(key))
            )  # находим максимум величины скидки в словаре
            if highest_discounts.filter(id=discount_choice[max_key]):
                data["discount"] = highest_discounts.filter(id=discount_choice[max_key])
            return data

        # если нет скидок на корзину и наборы, берём самые тяжелые скидки на продукты
        if data.get("product_discounts"):
            qs = data.get("product_discounts")
            highest_discounts = qs.filter(
                weight=qs.aggregate(max_weight=Max("weight"))["max_weight"]
            )  # берем самые "тяжелые" скидки
            data["discount"] = highest_discounts
            return data

    def calculate_discount_price_product(self, products, total_price, base_price=None):
        """
        Рассчитать цену со скидкой на товар с дополнительным необязательным параметром Цена товара
        """
        data = self.get_priority_discount(products, total_price)
        result = []

        # для скидок на корзину и наборы

        if data and data.get("discount"):
            if data.get("discount")[0].type != 'p':
                discounts = data.get("discount")
                discount = discounts[0]

                if discount.type == "c":  # если на корзину
                    if discount.percent:
                        price_with_discount = total_price - round(total_price * Decimal(discount.percent / 100), 2)
                    else:
                        price_with_discount = total_price - discount.discount_volume
                    if base_price and price_with_discount < base_price:
                        price_with_discount = base_price
                    elif not base_price and price_with_discount < Decimal(1):
                        price_with_discount = Decimal(1)
                    result.append(price_with_discount)
                    result.append(discounts)
                    return result

                if discount.type == "s":  # если на набор
                    set_price = Decimal(0)  # added Decimal
                    for product_seller in data["products"]:
                        if product_seller.product in discount.products.all() or product_seller.product.category in discount.categories.all():
                            set_price += Decimal(product_seller.price)  # added Decimal
                    if discount.percent:
                        discount_volume = round(set_price * discount.percent / 100, 2)
                    else:
                        discount_volume = discount.discount_volume
                    set_price_with_discount = set_price - discount_volume
                    if base_price and set_price_with_discount < base_price:
                        price_with_discount = total_price - Decimal(set_price) + base_price
                    elif not base_price and set_price_with_discount < Decimal(1):
                        price_with_discount = total_price - set_price + Decimal(1)
                    else:
                        price_with_discount = total_price - set_price + set_price_with_discount
                    result.append(price_with_discount)
                    result.append(discounts)
                    return result
            else:  # для скидок на продукты
                discounts = data.get("discount")
                top_discounts = {}
                for discount in discounts:
                    set_price = 0
                    count = 0
                    for item in data["products_pcs"]:
                        if item[0] in discount.products.all() or item[0].product.category in discount.categories.all():
                            set_price += (item[0].price * item[1])
                            count += item[1]
                    if discount.percent:
                        total_discount = round(set_price * discount.percent / 100,  # deleted Decimal(disc..../100)
                                               2)  # величина скидки, если указан процент
                        top_discounts[discount] = total_discount
                    elif discount.discount_volume:
                        total_discount = discount.discount_volume * count  # величина скидки, если указан уровень
                        top_discounts[discount] = total_discount

                top_discounts = sorted(top_discounts.items(), key=lambda x: x[1],
                                       reverse=True)  # сортируем скидки в порядке убвания величины скидки (список кортежей)
                discount_sum = Decimal(0)  # added Decimal(0)
                used_discounts = []
                for discount in top_discounts:
                    print(data["products_pcs"])
                    for item in data["products_pcs"]:
                        print(item[0], item[0] in discount[0].products.all(), discount[0].products.all())
                        print(item[0].product.category, item[0].product.category in discount[0].categories.all(), discount[0].categories.all())
                        if (item[0] in discount[0].products.all() or
                                item[0].product.category in discount[0].categories.all()):
                            if discount[0].percent:
                                discount_sum += (round(item[0].price * discount[0].percent / 100, 2) * item[1])  # deleted Decimal(discount[0].percent / 100)
                                #print('111111', item[1], round(item[0].price * discount[0].percent / 100, 2))
                            else:
                                discount_sum += (discount[0].discount_volume * item[1])
                                #print('22222', item[1], discount[0].discount_volume)
                            #print(discount_sum)
                            data["products_pcs"].remove(item)  # удаляем продукт, на который была применена скидка
                            if discount[0] not in used_discounts:
                                used_discounts.append(discount[0])  # добавляем эту скидку в список применненныых
                print(data["products_pcs"])
                price_with_discount = total_price - discount_sum

                if base_price and price_with_discount < base_price:
                    price_with_discount = base_price
                elif not base_price and price_with_discount < Decimal(1):
                    price_with_discount = Decimal(1)
                result.append(price_with_discount)
                result.append(used_discounts)
        return result
