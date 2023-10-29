from decimal import Decimal

from cart_and_orders.models import DeliveryMethod, Order, OrderProduct, StatusOrder
from cart_and_orders.services.orders import CompletedOrdersService
from cart_and_orders.utils.get_total_price import (
    get_total_delivery_price,
    get_total_price_with_discount,
)
from django.contrib.auth import get_user_model
from django.test import TestCase
from shopapp.models import Category, Product, ProductSeller, Seller


class SetUpClass(TestCase):
    """
    Класс для формирования метода setUp, чтоб затем наследовать его в других тестах
    """

    def setUp(self):
        # тестовый пользователь
        self.user = get_user_model().objects.create_user(
            name="testuser",
            password="testpassword",
            email="123@skill.box",
        )
        # тестовый пользователь без заказов
        self.user_with_no_orders = get_user_model().objects.create_user(
            name="testuser2",
            password="testpassword",
            email="321@skill.box",
        )
        # способ доставки
        self.delivery_method = DeliveryMethod.objects.create(
            name="Обычная", price=Decimal("200"), order_minimal_price=Decimal("2000")
        )
        # тестовые продавцы
        self.seller = Seller.objects.create(
            user=None,
            name="Seller Name",
            slug="seller-slug",
            image="path/to/seller/image.jpg",
            delivery_method="Some Delivery Method",
            payment_method="Some Payment Method",
            description="Seller Description",
            email="seller@example.com",
            phone="1234567890",
            address="Seller Address",
        )

        self.another_seller = Seller.objects.create(
            user=None,
            name="Another Seller Name",
            slug="seller-slug",
            image="path/to/seller/image.jpg",
            delivery_method="Some Delivery Method",
            payment_method="Some Payment Method",
            description="Seller Description",
            email="seller@example.com",
            phone="1234567890",
            address="Seller Address",
        )
        # тестовая категория
        self.category = Category.objects.create(
            name="CName",
        )
        # тестовый продукт
        self.product = Product.objects.create(
            category=self.category,
            name="Name",
            slug="slug",
            description="Description",
            available=True,
        )
        # тестовые товары у продавца
        self.product_seller = ProductSeller.objects.create(
            product=self.product,
            seller=self.seller,
            price=Decimal("500"),
            quantity=5,
            free_delivery=True,
            is_limited_edition=False,
        )

        self.another_product_seller = ProductSeller.objects.create(
            product=self.product,
            seller=self.another_seller,
            price=Decimal("1000"),
            quantity=1,
            free_delivery=True,
            is_limited_edition=False,
        )
        # тестовые заказы
        self.order = Order.objects.create(
            city="City",
            address="Address",
            delivery_method=self.delivery_method,
            payment_method="Online",
            total_price=Decimal("50.00"),
            status=StatusOrder.CREATED,
        )
        # тестовые выполненные заказы
        self.order1 = Order.objects.create(
            user=self.user,
            city="City1",
            address="Address1",
            status="delivered",
            payment_method="Online",
        )

        self.order2 = Order.objects.create(
            user=self.user,
            city="City2",
            address="Address2",
            status="created",
            payment_method="Online",
        )

        self.order3 = Order.objects.create(
            user=self.user,
            city="City3",
            address="Address3",
            status="delivered",
            payment_method="Online",
        )
        # тестовые элементы заказа
        self.order_product = OrderProduct.objects.create(
            order=self.order,
            product=self.product_seller.product,
            seller=self.product_seller.seller,
            quantity=5,
            price=self.product_seller.price,
        )

        self.another_order_product = OrderProduct.objects.create(
            order=self.order,
            product=self.another_product_seller.product,
            seller=self.another_product_seller.seller,
            quantity=1,
            price=self.another_product_seller.price,
        )


class TotalPriceTestCase(SetUpClass):
    """
    Тест для проверки подсчета полной цены заказа
    """

    def SetUp(self):
        super().setUp()

    def test_get_total_price_with_discount(self):
        total_price = get_total_price_with_discount(self.order.id)
        self.assertEqual(total_price, Decimal("3500"))

    def test_get_total_price_delivery(self):
        total_price_delivery = get_total_delivery_price(self.order.id)
        self.assertEqual(total_price_delivery, Decimal("200"))


class CompletedOrdersServiceTest(SetUpClass):
    """
    Тест для проверки выполненных заказов
    """

    def setUp(self):
        super().setUp()

    def test_get_orders_returns_delivered_orders(self):
        completed_orders = CompletedOrdersService.get_orders(self.user)
        self.assertEqual(len(completed_orders), 2)  # Проверяем, что вернулись два завершенных заказа
        self.assertIn(self.order1, completed_orders)  # Проверяем, что первый заказ в списке
        self.assertIn(self.order3, completed_orders)  # Проверяем, что третий заказ в списке

    def test_get_orders_returns_empty_list_for_user_with_no_completed_orders(self):
        completed_orders = CompletedOrdersService.get_orders(self.user_with_no_orders)
        self.assertEqual(len(completed_orders), 0)  # Проверяем, что вернулся пустой список


class CartServiceTest(SetUpClass):
    """
    Тест для проверки методов корзины
    """

    def setUp(self):
        super().setUp()

    def test_get_cart(self):
        """
        Тест получения корзины
        """
        response = self.client.get("/cart/")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Товары еще не добавлены в корзину")

    def test_add_product_to_cart(self):
        """
        Тест добавления товара в корзину для неавторизованного пользователя
        """
        self.client.session["cart"] = {}
        product_seller = self.product_seller
        response = self.client.post(f"/cart/add/{product_seller.id}", data={})
        self.assertEquals(response.status_code, 301)
        response = self.client.get("/cart/")

        self.assertContains(response, product_seller.product.name)

    def test_change_quantity_product_to_cart(self):
        """
        Тест изменения кол-ва товара в корзине для неавторизованного пользователя
        """
        initial_quantity = 5
        cart = self.client.session.get("cart", {})
        cart[self.product_seller.id] = initial_quantity
        self.client.session["cart"] = cart

        new_quantity = 10
        response = self.client.post(
            f"/cart/change_quantity/{self.product_seller.id}", data={"order_quantity": new_quantity}
        )
        self.assertEquals(response.status_code, 301)

        response = self.client.get("/cart/")
        self.assertContains(response, str(new_quantity))

    def test_delete_product_from_cart(self):
        """
        Тест удаления товара из корзине для неавторизованного пользователя
        """
        cart = self.client.session.get("cart", {})
        product_id = self.product_seller.id
        cart[product_id] = 1
        self.client.session["cart"] = cart

        response = self.client.get(f"/cart/remove/{product_id}")
        self.assertEquals(response.status_code, 301)

        self.client.session.modified = True
        cart = self.client.session.get("cart", {})

        self.assertTrue(cart == {})

    def test_clear_cart(self):
        """
        Тест очистки корзины для неавторизованного пользователя
        """
        cart = self.client.session.get("cart", {})
        product_id = self.product_seller.id
        cart[product_id] = 1
        self.client.session["cart"] = cart

        response = self.client.get("/cart/clear/", HTTP_REFERER="/cart/")
        self.assertEquals(response.status_code, 302)

        self.client.session.modified = True
        cart = self.client.session.get("cart", {})

        self.assertTrue(cart == {})
