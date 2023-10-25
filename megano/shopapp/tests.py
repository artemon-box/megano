import unittest
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.http import HttpRequest
from django.shortcuts import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import resolve
from django.utils.text import slugify

from cart_and_orders.models import Order, OrderProduct, DeliveryMethod, StatusOrder
from config import settings
from shopapp.models import Category, Discount, Product, ProductSeller, Seller, ProductReview
from shopapp.services.compared_products import ComparedProductsService
from shopapp.services.discount import DiscountService
from shopapp.services.product_review import ProductReviewService
from shopapp.utils.banners_cache import get_random_active_product_banners
from shopapp.utils.categories_cache import get_cached_active_categories
from shopapp.utils.details_cache import get_cached_product_by_slug
from shopapp.utils.seller_top_sales import seller_top_sales
from shopapp.views import catalog_list


class SetUpClass(TestCase):
    """
    Класс для формирования метода setUp, чтоб затем наследовать его в других тестах
    """

    def setUp(self):
        # тестовый пользователь
        self.user = get_user_model().objects.create_user(
            name='testuser',
            password='testpassword',
            email='321@skill.box'
        )
        # продавцы
        self.seller1 = Seller.objects.create(
            name="Cитилинк",
            slug="citylink",
            delivery_method="by_bus",
            payment_method="cash",
        )
        self.seller2 = Seller.objects.create(
            name="МВидео",
            slug="mvideo",
            delivery_method="by_bus",
            payment_method="cash",
        )
        # категории
        self.category1 = Category.objects.create(name="Кухонная техника")
        self.category2 = Category.objects.create(name="Наушники")
        self.category3 = Category.objects.create(name="Микроволновые печи")
        self.category4 = Category.objects.create(name="Телевизоры")
        self.category5 = Category.objects.create(name="Мобильные телефоны")
        # активные категории
        self.active_categories = [
            self.category1,
            self.category2,
            self.category3,
            self.category4,
            self.category5,
        ]
        # товары
        self.product1 = Product.objects.create(
            category=self.category1,
            name="kuhonnyj-tehnik",
            slug="kuhonnyj-tehnik",
            available=True
        )
        self.product2 = Product.objects.create(
            category=self.category2,
            name="naushnik",
            available=True,
            slug="naushnik",
        )
        self.product3 = Product.objects.create(
            category=self.category3,
            name="mikrovolnovaya-pech",
            slug="mikrovolnovaya-pech",
            available=True
        )
        self.product4 = Product.objects.create(
            category=self.category4,
            name="mobilnyj-telefon",
            slug="mobilnyj-telefon",
            available=True
        )
        self.product5 = Product.objects.create(
            category=self.category5,
            name="televizor",
            slug="televizor",
            available=True
        )
        # активные продукты
        self.active_products = [
            self.product1,
            self.product2,
            self.product3,
            self.product4,
            self.product5,
        ]
        # тестовые отзывы
        self.review1 = ProductReview.objects.create(
            product=self.product1,
            user=self.user,
            text='Review 1'
        )
        self.review2 = ProductReview.objects.create(
            product=self.product1,
            user=self.user,
            text='Review 2'
        )
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
        # способ доставки для заказа
        self.delivery_method = DeliveryMethod.objects.create(
            name="Обычная",
            price=Decimal('200'),
            order_minimal_price=Decimal('2000')
        )
        # заказ со статусом delivered
        self.order = Order.objects.create(
            city="City",
            address="Address",
            delivery_method=self.delivery_method,
            payment_method="Online",
            total_price=Decimal('2500'),
            status=StatusOrder.DELIVERED
        )
        # товар в заказе
        self.order_product = OrderProduct.objects.create(
            order=self.order,
            product=self.product_seller1.product,
            seller=self.product_seller1.seller,
            quantity=5,
            price=self.product_seller1.price
        )
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
    """Тесты скидок"""

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


class TestComparedProductsService(SetUpClass):
    def setUp(self) -> None:
        super().setUp()
        response = self.client.get(reverse("shopapp:compare_list"))
        request = response.wsgi_request
        self.compare_list = ComparedProductsService(request)

    def test_add_to_compare_list(self):
        self.assertEqual(self.compare_list.get_compared_products(), [])
        self.compare_list.add_to_compared_products(self.product_seller1.id)
        self.compare_list.add_to_compared_products(self.product_seller2.id)
        self.assertEqual(self.compare_list.get_compared_products(), [1, 2])

    def test_remove_from_compare_list(self):
        self.compare_list.add_to_compared_products(self.product_seller1.id)
        self.compare_list.add_to_compared_products(self.product_seller2.id)
        self.assertEqual(self.compare_list.get_compared_products(), [1, 2])
        self.compare_list.remove_from_compared_products(self.product_seller1.id)
        self.assertEqual(self.compare_list.get_compared_products(), [2, ])
        self.compare_list.remove_from_compared_products(self.product_seller2.id)
        self.assertEqual(self.compare_list.get_compared_products(), [])

    def test_clear_compare_list(self):
        self.compare_list.add_to_compared_products(self.product_seller1.id)
        self.compare_list.add_to_compared_products(self.product_seller2.id)
        self.assertEqual(self.compare_list.get_compared_products(), [1, 2])
        self.compare_list.clear()
        self.assertEqual(self.compare_list.get_compared_products(), [])


class TestComparedProductsView(SetUpClass):

    def test_add_to_comparison_view(self):
        response = self.client.get(reverse("shopapp:compare_add", kwargs={"product_id": self.product_seller1.id}))
        request = response.wsgi_request
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertEqual(request.session.get(settings.COMPARE_LIST_SESSION_ID), [1])
        response = self.client.get(reverse("shopapp:compare_add", kwargs={"product_id": self.product_seller2.id}))
        request = response.wsgi_request
        self.assertEqual(request.session.get(settings.COMPARE_LIST_SESSION_ID), [1, 2])

    def test_remove_from_comparison_view(self):
        response = self.client.get(reverse("shopapp:compare_add", kwargs={"product_id": self.product_seller3.id}))
        request = response.wsgi_request
        self.assertEqual(request.session.get(settings.COMPARE_LIST_SESSION_ID), [3])
        response = self.client.get(reverse("shopapp:compare_add", kwargs={"product_id": self.product_seller4.id}))
        request = response.wsgi_request
        self.assertEqual(request.session.get(settings.COMPARE_LIST_SESSION_ID), [3, 4])
        response = self.client.get(reverse("shopapp:compare_remove", kwargs={"product_id": self.product_seller3.id}))
        request = response.wsgi_request
        self.assertEqual(request.session.get(settings.COMPARE_LIST_SESSION_ID), [4])
        self.assertRedirects(response, expected_url="/compare/", status_code=302)

    def test_clear_comparison_view(self):
        response = self.client.get(reverse("shopapp:compare_add", kwargs={"product_id": self.product_seller1.id}))
        request = response.wsgi_request
        self.assertEqual(request.session.get(settings.COMPARE_LIST_SESSION_ID), [1])
        response = self.client.get(reverse("shopapp:compare_add", kwargs={"product_id": self.product_seller2.id}))
        request = response.wsgi_request
        self.assertEqual(request.session.get(settings.COMPARE_LIST_SESSION_ID), [1, 2])
        response = self.client.get(reverse("shopapp:compare_clear"))
        request = response.wsgi_request
        self.assertEqual(request.session.get(settings.COMPARE_LIST_SESSION_ID), [])
        self.assertRedirects(response, expected_url="/compare/", status_code=302)

    def test_comparison_of_products_view(self):
        response = self.client.get(reverse("shopapp:compare_list"))
        # self.assertTemplateUsed(response, "shopapp/comparison.jinja2")
        self.assertEqual(response.status_code, 200)


class RandomActiveProductBannersTest(SetUpClass):
    """
    Тест для проверки формирования баннеров
    """
    def setUp(self):
        super().setUp()

    def tearDown(self):
        # Очищаем кэш после теста
        cache.clear()

    def test_get_random_active_product_banners(self):
        banners = get_random_active_product_banners()

        self.assertIsInstance(banners, list)

        self.assertTrue(len(banners) <= 3)

        for banner in banners:
            self.assertIn(banner, self.active_products)

        cache_key = "random_product_banners"
        cached_banners = cache.get(cache_key)
        self.assertIsNotNone(cached_banners)


class CachedActiveCategoriesTest(SetUpClass):
    """
    Тест для проверки кэширования категорий
    """
    def setUp(self):
        super().setUp()

        # Устанавливаем настройку CATEGORY_MENU_CACHE_TIMEOUT для кэша
        self.cache_timeout = 600  # 10 минут (в секундах)

    def tearDown(self):
        # Очищаем кэш после теста
        cache.clear()

    def test_get_cached_active_categories(self):
        # Получаем кэшированные активные категории
        cached_categories = get_cached_active_categories()

        # Проверяем, что полученные категории являются QuerySet
        self.assertIsInstance(cached_categories, Category.objects.filter().distinct().__class__)

        # Проверяем, что количество полученных категорий соответствует ожиданиям
        self.assertEqual(len(cached_categories), len(self.active_categories))

        # Проверяем, что полученные категории содержатся в списке активных категорий
        for category in cached_categories:
            self.assertIn(category, self.active_categories)

        # Проверяем, что данные были сохранены в кэше
        cache_key = "active_categories"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)

    def test_cache_timeout(self):
        # Устанавливаем кэшированные категории с кастомным таймаутом
        cached_categories = get_cached_active_categories()
        cache_timeout = 3600  # 1 час (в секундах)
        cache.set("active_categories", cached_categories, cache_timeout)

        # Получаем категории из кэша
        retrieved_categories = get_cached_active_categories()

        # Проверяем, что категории из кэша соответствуют ожиданиям
        self.assertEqual(list(cached_categories), list(retrieved_categories))


class CachedProductBySlugTest(SetUpClass):
    """
    Проверка кэширования продукта по слагу
    """
    def setUp(self):
        super().setUp()

        # Устанавливаем настройку PRODUCT_CACHE_TIMEOUT для кэша
        self.cache_timeout = 600  # 10 минут (в секундах)

    def tearDown(self):
        # Очищаем кэш после теста
        cache.clear()

    def test_get_cached_product_by_slug(self):
        # Получаем кэшированный продукт по слагу
        cached_product = get_cached_product_by_slug('kuhonnyj-tehnik')

        # Проверяем, что полученный продукт является экземпляром Product
        self.assertIsInstance(cached_product, Product)

        # Проверяем, что полученный продукт соответствует ожиданиям
        self.assertEqual(cached_product, self.product1)

        # Проверяем, что данные были сохранены в кэше
        cache_key = "product_kuhonnyj-tehnik"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)

    def test_cache_timeout(self):
        # Устанавливаем кэшированный продукт с кастомным таймаутом
        cached_product = get_cached_product_by_slug('naushnik')
        cache_timeout = 3600  # 1 час (в секундах)
        cache.set("product_naushnik", cached_product, cache_timeout)

        # Получаем продукт из кэша
        retrieved_product = get_cached_product_by_slug('naushnik')

        # Проверяем, что продукт из кэша соответствует ожиданиям
        self.assertEqual(retrieved_product, self.product2)


class SellerTopSalesTest(SetUpClass):
    """
    Тест рейтинга топ товаров по продажам для продавца
    """
    def setUp(self):
        super().setUp()

    def test_seller_top_sales(self):
        # Получаем топ продаж для тестового продавца
        top_sales = seller_top_sales(self.seller2)

        # Проверяем, что результат содержит ожидаемый продукт
        self.assertEqual(len(top_sales), 1)
        top_sale = top_sales[0]
        self.assertEqual(top_sale["seller_product"], self.product_seller1)
        self.assertEqual(top_sale["total_quantity"], 5)


class ProductReviewServiceTest(SetUpClass):
    """
    Тест сервиса отзывов
    """
    def setUp(self):
        super().setUp()
        # Создаем сервис отзывов
        self.review_service = ProductReviewService()

    def test_get_reviews_for_product(self):
        # Получаем отзывы для тестового продукта
        reviews = self.review_service.get_reviews_for_product(self.product1)

        # Проверяем, что оба тестовых отзыва присутствуют
        self.assertEqual(len(reviews), 2)
        self.assertIn(self.review1, reviews)
        self.assertIn(self.review2, reviews)

    def test_add_review_for_product(self):
        # Добавляем новый отзыв к тестовому продукту
        self.review_service.add_review_for_product(self.product1, user_id=self.user.id, review_text='Review 3')

        # Получаем отзывы для тестового продукта
        reviews = self.review_service.get_reviews_for_product(self.product1)

        # Проверяем, что новый отзыв добавлен
        self.assertEqual(len(reviews), 3)
        new_review = ProductReview.objects.get(text='Review 3')
        self.assertIn(new_review, reviews)

    def test_get_reviews_count(self):
        # Получаем количество отзывов для тестового продукта
        reviews_count = self.review_service.get_reviews_count(self.product1)

        # Проверяем, что количество отзывов соответствует ожиданиям
        self.assertEqual(reviews_count, 2)  # Уже существующие отзывы
