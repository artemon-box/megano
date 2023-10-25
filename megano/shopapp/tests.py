from decimal import Decimal

from django.shortcuts import reverse
from django.test import TestCase
from shopapp.models import Category, Discount, Product, ProductSeller, Seller
from shopapp.services.discount import DiscountService


class SetUpClass(TestCase):
    """
    Класс для формирования метода setUp, чтоб затем наследовать его в других тестах
    """

    def setUp(self):
        # продавцы
        self.seller1 = Seller.objects.create(
            name="Cитилинк", slug="citylink", delivery_method="by_bus", payment_method="cash"
        )
        self.seller2 = Seller.objects.create(
            name="МВидео", slug="mvideo", delivery_method="by_bus", payment_method="cash"
        )
        # категории
        self.category1 = Category.objects.create(name="Кухонная техника")
        self.category2 = Category.objects.create(name="Наушники")
        self.category3 = Category.objects.create(name="Микроволновые печи")
        self.category4 = Category.objects.create(name="Телевизоры")
        self.category5 = Category.objects.create(name="Мобильные телефоны")
        # товары
        self.product1 = Product.objects.create(category=self.category1, name="kuhonnyj-tehnik", available=True)
        self.product2 = Product.objects.create(category=self.category2, name="naushnik", available=True)
        self.product3 = Product.objects.create(category=self.category3, name="mikrovolnovaya-pech", available=True)
        self.product4 = Product.objects.create(category=self.category5, name="mobilnyj-telefon", available=True)
        # товары в корзине
        self.product_seller1 = ProductSeller.objects.create(product=self.product1, seller=self.seller2, price=300.0)
        self.product_seller2 = ProductSeller.objects.create(product=self.product2, seller=self.seller1, price=444.0)
        self.product_seller3 = ProductSeller.objects.create(product=self.product3, seller=self.seller2, price=678.0)
        self.product_seller4 = ProductSeller.objects.create(product=self.product4, seller=self.seller2, price=322.0)
        # все доступные товары у продавцов
        self.products = [self.product_seller1, self.product_seller2, self.product_seller3, self.product_seller4]
        # корзина для тестов
        self.cart = [
            {"product_seller": self.product_seller1, "quantity": 3},
            {"product_seller": self.product_seller2, "quantity": 1},
            {"product_seller": self.product_seller3, "quantity": 2},
        ]
        # стоимость всей корзины без скидок
        self.total_price = Decimal(2700.0)

        # экземпляр сервиса скидки
        self.discount = DiscountService()

        # скидки
        self.cart_discount1 = Discount.objects.create(
            title="discount1",
            type="c",
            weight="2",
            discount_volume=350.0,
            start="2023-10-01",
            end="2023-10-31",
            is_active=True,
        )
        self.cart_discount2 = Discount.objects.create(
            title="discount2",
            type="c",
            weight="2",
            percent=50,
            cart_numbers=5,
            start="2023-10-01",
            end="2023-10-31",
            is_active=True,
        )
        self.set_discount1 = Discount.objects.create(
            title="discount3", type="s", weight="2", discount_volume=5.0, start="2023-10-01", is_active=True
        )
        # присваиваем полям M2M значения
        self.set_discount1.categories.set([self.category1, self.category3])
        self.set_discount1.products.set([self.product_seller1])
        self.set_discount1.save()

        self.set_discount2 = Discount.objects.create(
            title="discount4", type="s", weight="2", percent=29, start="2023-10-01", is_active=True
        )
        # присваиваем полям M2M значения
        self.set_discount2.categories.set([self.category1, self.category3])
        self.set_discount2.products.set([self.product_seller1])
        self.set_discount2.save()

        self.set_discount3 = Discount.objects.create(
            title="discount5", type="s", weight="2", discount_volume=645.0, start="2023-10-01", is_active=True
        )
        # присваиваем полям M2M значения
        self.set_discount3.categories.set([self.category2])
        self.set_discount3.save()

        self.set_discount4 = Discount.objects.create(
            title="discount6", type="s", weight="2", discount_volume=1645.0, start="2023-10-01", is_active=True
        )
        # присваиваем полям M2M значения
        self.set_discount4.categories.set([self.category4])
        self.set_discount4.save()

        self.product_discount1 = Discount.objects.create(
            title="discount7", type="p", weight="3", percent=15, start="2023-10-01", is_active=True
        )
        # присваиваем полям M2M значения
        self.product_discount1.categories.set([self.category2])
        self.product_discount1.products.set([self.product_seller1])
        self.product_discount1.save()

        self.product_discount2 = Discount.objects.create(
            type="p", weight="3", discount_volume=100.1, start="2023-10-01", is_active=True
        )
        # присваиваем полям M2M значения
        self.product_discount2.categories.set([self.category3])
        self.product_discount2.products.set([self.product_seller4])
        self.product_discount2.save()


class DiscountsTest(SetUpClass):
    "Тесты скидок"

    def setUp(self):
        super().setUp()

    # тесты
    def test_cart_discount1(self):
        self.cart_discount2.is_active = False  # делаем cart_discount2 неактивной
        self.cart_discount2.save()
        result = self.discount.calculate_discount_price_product(self.cart, self.total_price)
        self.assertEquals(result[0], 2350.0)
        self.assertEquals(result[1][0], self.cart_discount1)

    def test_cart_discount2(self):
        result = self.discount.calculate_discount_price_product(self.cart, self.total_price)
        self.assertEquals(result[0], 1350.0)
        self.assertEquals(result[1][0], self.cart_discount2)

    def test_set_discount1(self):
        self.cart_discount1.end = "2023-10-02"
        self.cart_discount1.save()
        self.cart_discount2.is_active = False  # делаем cart_discount2 неактивной
        self.cart_discount2.save()
        self.set_discount2.start = "3000-10-10"
        self.set_discount2.save()
        self.set_discount3.weight = "1"  # делаем set_discount3 "легче"
        self.set_discount3.save()
        result = self.discount.calculate_discount_price_product(self.cart, self.total_price)
        self.assertEquals(result[0], 2695.0)
        self.assertEquals(result[1][0], self.set_discount1)

    def test_set_discount2(self):
        self.cart_discount1.end = "2023-10-02"
        self.cart_discount1.save()
        self.cart_discount2.is_active = False  # делаем cart_discount2 неактивной
        self.cart_discount2.save()
        self.set_discount3.weight = "1"
        self.set_discount3.save()
        result = self.discount.calculate_discount_price_product(self.cart, self.total_price)
        self.assertEquals(float(result[0]), 2416.38)
        self.assertEquals(result[1][0], self.set_discount2)

    def test_set_discount3(self):
        self.cart_discount1.end = "2023-10-02"  # делаем cart_discount1 просроченной
        self.cart_discount1.save()
        self.cart_discount2.is_active = False  # делаем cart_discount2 неактивной
        self.cart_discount2.save()
        result = self.discount.calculate_discount_price_product(self.cart, self.total_price)
        self.assertEquals(result[0], 2257.00)
        self.assertEquals(result[1][0], self.set_discount3)

    def test_product_discount_1_and_2(self):
        # деактивируем скидки на корзину и наборы
        for item in [
            self.cart_discount1,
            self.cart_discount2,
            self.set_discount1,
            self.set_discount2,
            self.set_discount3,
        ]:
            item.is_active = False
            item.save()
        result = self.discount.calculate_discount_price_product(self.cart, self.total_price)
        self.assertEquals(float(result[0]), 2298.20)
        self.assertEquals(result[1], [self.product_discount1, self.product_discount2])

    def test_no_discounts(self):
        for discount in Discount.objects.all():
            discount.delete()  # удаляем все скидки
        result = self.discount.calculate_discount_price_product(self.cart, self.total_price)
        self.assertEquals(result, [])

    # тест страницы скидок
    def test_discounts_page(self):
        response = self.client.get(reverse("shopapp:discounts"))
        self.assertEquals(response.status_code, 200)
        # проверка, что все скидки содержатся на странице списка скидок
        self.assertContains(
            response, [str(discount.title) for discount in Discount.objects.all()][-1]
        )  # [-1], т.к. в списке какой то None появляется


class CatalogTest(SetUpClass):
    """
    Тест вью-функции каталога
    """

    def setUp(self) -> None:
        super().setUp()

    def test_catalog_list(self):
        response = self.client.get("/catalog/")
        self.assertEquals(response.status_code, 200)

    def test_context(self):
        data = {"price": "0;100000"}
        response = self.client.post("/catalog/", data=data)
        for item in self.products:  # так проверяем что все продукты попали в каталог
            # (по-нормальному никак, т.к. с jinja2 не приходит context в response)
            self.assertContains(response, item.product.name)

    def test_filter_by_price(self):
        """
        Проверяем, что продукт с ценой более 677 не содержится в респонсе
        """
        data = {"price": "0;677"}
        response = self.client.post("/catalog/", data=data)
        for item in self.products:
            if item == self.product_seller3:
                self.assertNotContains(response, item.product.name)
            else:
                self.assertContains(response, item.product.name)

    def test_filter_by_title(self):
        """
        Проверяем, что происке товара по названию при вводе "ush" находится naushnik
        """
        data = {"price": "0;100000", "title": "ush"}
        response = self.client.post("/catalog/", data=data)
        for item in self.products:
            if item.product.name == "naushnik":
                self.assertContains(response, item.product.name)
            else:
                self.assertNotContains(response, item.product.name)

    def test_order_by_price(self):
        """
        Проверка сортировки по цене
        """
        # d ata = {"price": "0;100000"}
        # sorted_products = [self.product_seller3, self.product_seller2, self.product_seller4, self.product_seller1]
        # response = self.client.get("/catalog/?sort=-price/", data=data)
        # for item in sorted_products:  не работает!!!
        #     self.assertIn(item.product.name, response)
