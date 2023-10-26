from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from cart_and_orders.models import Order, OrderProduct, DeliveryMethod, StatusOrder
from cart_and_orders.services.orders import CompletedOrdersService

from cart_and_orders.utils.get_total_price import get_total_price, get_total_price_delivery
from shopapp.models import Seller, Product, ProductSeller, Category


class SetUpClass(TestCase):
    """
    Класс для формирования метода setUp, чтоб затем наследовать его в других тестах
    """
    def setUp(self):
        # тестовый пользователь
        self.user = get_user_model().objects.create_user(
            name='testuser',
            password='testpassword',
            email='123@skill.box',
        )
        # тестовый пользователь без заказов
        self.user_with_no_orders = get_user_model().objects.create_user(
            name='testuser2',
            password='testpassword',
            email='321@skill.box',
        )
        # способ доставки
        self.delivery_method = DeliveryMethod.objects.create(
            name="Обычная",
            price=Decimal('200'),
            order_minimal_price=Decimal('2000')
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
            address="Seller Address"
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
            address="Seller Address"
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
            price=Decimal('500'),
            quantity=5,
            free_delivery=True,
            is_limited_edition=False
        )

        self.another_product_seller = ProductSeller.objects.create(
            product=self.product,
            seller=self.another_seller,
            price=Decimal('1000'),
            quantity=1,
            free_delivery=True,
            is_limited_edition=False
        )
        # тестовые заказы
        self.order = Order.objects.create(
            city="City",
            address="Address",
            delivery_method=self.delivery_method,
            payment_method="Online",
            total_price=Decimal('50.00'),
            status=StatusOrder.CREATED
        )
        # тестовые выполненные заказы
        self.order1 = Order.objects.create(
            user=self.user,
            city='City1',
            address='Address1',
            status='delivered',
            payment_method="Online",
        )

        self.order2 = Order.objects.create(
            user=self.user,
            city='City2',
            address='Address2',
            status='created',
            payment_method="Online",
        )

        self.order3 = Order.objects.create(
            user=self.user,
            city='City3',
            address='Address3',
            status='delivered',
            payment_method="Online",
        )
        # тестовые элементы заказа
        self.order_product = OrderProduct.objects.create(
            order=self.order,
            product=self.product_seller.product,
            seller=self.product_seller.seller,
            quantity=5,
            price=self.product_seller.price
        )

        self.another_order_product = OrderProduct.objects.create(
            order=self.order,
            product=self.another_product_seller.product,
            seller=self.another_product_seller.seller,
            quantity=1,
            price=self.another_product_seller.price
        )


class TotalPriceTestCase(SetUpClass):
    """
    Тест для проверки подсчета полной цены заказа
    """

    def SetUp(self):
        super().setUp()

    def test_get_total_price(self):
        total_price = get_total_price(self.order.id)
        self.assertEqual(total_price, Decimal('3500'))

    def test_get_total_price_delivery(self):
        total_price_delivery = get_total_price_delivery(self.order.id)
        self.assertEqual(total_price_delivery, Decimal('3700'))


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
