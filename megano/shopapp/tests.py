from django.test import TestCase
from decimal import Decimal
from shopapp.models import Discount, ProductSeller, Product, Seller, Category
from shopapp.services.discount import DiscountService


class DiscountsTest(TestCase):
    "Тесты скидок"

    def setUp(self):
        # продавцы
        self.seller1 = Seller.objects.create(
            name="Cитилинк",
            slug="citylink",
            delivery_method="by_bus",
            payment_method="cash"
        )
        self.seller2 = Seller.objects.create(
            name="МВидео",
            slug="mvideo",
            delivery_method="by_bus",
            payment_method="cash"
        )
        # категории
        self.category1 = Category.objects.create(
            name="Кухонная техника"
        )
        self.category2 = Category.objects.create(
            name="Наушники"
        )
        self.category3 = Category.objects.create(
            name="Микроволновые печи"
        )
        self.category4 = Category.objects.create(
            name="Телевизоры"
        )
        self.category5 = Category.objects.create(
            name="Мобильные телефоны"
        )
        # товары
        self.product1 = Product.objects.create(
            category=self.category1,
            name="Кухонный техник",
            available=True
        )
        self.product2 = Product.objects.create(
            category=self.category2,
            name="Наушник",
            available=True
        )
        self.product3 = Product.objects.create(
            category=self.category3,
            name="Микроволновая печь",
            available=True
        )
        self.product4 = Product.objects.create(
            category=self.category5,
            name="Мобильный телефон",
            available=True
        )
        # товары в корзине
        self.product_seller1 = ProductSeller.objects.create(
            product=self.product1,
            seller=self.seller2,
            price=300.0
        )
        self.product_seller2 = ProductSeller.objects.create(
            product=self.product2,
            seller=self.seller1,
            price=444.0
        )
        self.product_seller3 = ProductSeller.objects.create(
            product=self.product3,
            seller=self.seller2,
            price=678.0
        )
        self.product_seller4 = ProductSeller.objects.create(
            product=self.product4,
            seller=self.seller2,
            price=322.0
        )
        # корзина для тестов
        self.cart = [
            {"product_seller": self.product_seller1, "quantity": 3},
            {"product_seller": self.product_seller2, "quantity": 1},
            {"product_seller": self.product_seller3, "quantity": 2}
        ]
        # стоимость всей корзины без скидок
        self.total_price = Decimal(2700.0)

        # экземпляр сервиса скидки
        self.discount = DiscountService()

        # скидки
        self.cart_discount1 = Discount.objects.create(
            type="c",
            weight="2",
            discount_volume=350.0,
            start="2023-10-01",
            end="2023-10-31",
            is_active=True
        )
        self.cart_discount2 = Discount.objects.create(
            type="c",
            weight="2",
            percent=50,
            cart_numbers=5,
            start="2023-10-01",
            end="2023-10-31",
            is_active=True
        )
        self.set_discount1 = Discount.objects.create(
            type="s",
            weight="2",
            discount_volume=5.0,
            start="2023-10-01",
            is_active=True
        )
        # присваиваем полям M2M значения
        self.set_discount1.categories.set([self.category1, self.category3])
        self.set_discount1.products.set([self.product_seller1])
        self.set_discount1.save()

        self.set_discount2 = Discount.objects.create(
            type="s",
            weight="2",
            percent=29,
            start="2023-10-01",
            is_active=True
        )
        # присваиваем полям M2M значения
        self.set_discount2.categories.set([self.category1, self.category3])
        self.set_discount2.products.set([self.product_seller1])
        self.set_discount2.save()

        self.set_discount3 = Discount.objects.create(
            type="s",
            weight="2",
            discount_volume=645.0,
            start="2023-10-01",
            is_active=True
        )
        # присваиваем полям M2M значения
        self.set_discount3.categories.set([self.category2])
        self.set_discount3.save()

        self.set_discount4 = Discount.objects.create(
            type="s",
            weight="2",
            discount_volume=1645.0,
            start="2023-10-01",
            is_active=True
        )
        # присваиваем полям M2M значения
        self.set_discount4.categories.set([self.category4])
        self.set_discount4.save()

        self.product_discount1 = Discount.objects.create(
            type="p",
            weight="3",
            percent=15,
            start="2023-10-01",
            is_active=True
        )
        # присваиваем полям M2M значения
        self.product_discount1.categories.set([self.category2])
        self.product_discount1.products.set([self.product_seller1])
        self.product_discount1.save()

        self.product_discount2 = Discount.objects.create(
            type="p",
            weight="3",
            discount_volume=100.1,
            start="2023-10-01",
            is_active=True
        )
        # присваиваем полям M2M значения
        self.product_discount2.categories.set([self.category3])
        self.product_discount2.products.set([self.product_seller4])
        self.product_discount2.save()

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
        for item in [self.cart_discount1, self.cart_discount2, self.set_discount1,
                     self.set_discount2, self.set_discount3]:
            item.is_active = False
            item.save()
        result = self.discount.calculate_discount_price_product(self.cart, self.total_price)
        self.assertEquals(result[0], 2298.20)
        self.assertEquals(result[1], [self.product_discount1, self.product_discount2])
        #self.assertEquals(result[1][0], self.product_discount1)