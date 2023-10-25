from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from cart_and_orders.models import Order, OrderProduct, DeliveryMethod, StatusOrder
from paymentapp.utils.quantity_correction import quantity_correction
from shopapp.models import ProductSeller, Seller, Product, Category


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

        # тестовый продавец
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

        # тестовый продукт у продавца
        self.product_seller = ProductSeller.objects.create(
            product=self.product,
            seller=self.seller,
            price=Decimal('500'),
            quantity=10,
            free_delivery=True,
            is_limited_edition=False
        )
        # тестовый метод доставки
        self.delivery_method = DeliveryMethod.objects.create(
            name="Обычная",
            price=Decimal('200'),
            order_minimal_price=Decimal('2000')
        )

        # тестовый заказ
        self.order = Order.objects.create(
            city="City",
            address="Address",
            delivery_method=self.delivery_method,
            payment_method="Online",
            total_price=Decimal('2500'),
            status=StatusOrder.CREATED
        )

        # тестовый элемент заказа
        self.order_product = OrderProduct.objects.create(
            order=self.order,
            product=self.product_seller.product,
            seller=self.product_seller.seller,
            quantity=5,
            price=self.product_seller.price
        )


class QuantityCorrectionTest(SetUpClass):
    """
    Тест для проверки бизнес-логики
    """
    def SetUp(self):
        super().setUp()

    def test_quantity_correction_increases_quantity(self):
        quantity_correction(self.order.id, increase=True)

        self.product_seller.refresh_from_db()
        self.assertEqual(self.product_seller.quantity, 15)  # Проверяем, что количество товара увеличилось на 5

    def test_quantity_correction_decreases_quantity(self):
        quantity_correction(self.order.id, increase=False)

        self.product_seller.refresh_from_db()
        self.assertEqual(self.product_seller.quantity, 5)  # Проверяем, что количество товара уменьшилось на 5

