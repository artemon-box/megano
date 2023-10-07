from django.contrib.auth import get_user_model
from django.test import TestCase
from histviewapp.models import HistoryViewed
from histviewapp.services.history import HistoryService
from shopapp.models import Category, Product, ProductSeller, Seller


# Create your tests here.
class TestHistoryService(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email="testuser@skill.box", password="testpassword")
        category = Category.objects.create(name="testcategory")
        self.product1 = Product.objects.create(category=category, name="Product 1")
        self.product2 = Product.objects.create(category=category, name="Product 2")

    def test_add_product(self):
        self.assertFalse(HistoryService.is_product_watched(self.user, self.product1))
        HistoryService.add_product(self.user, self.product1)
        self.assertTrue(HistoryService.is_product_watched(self.user, self.product1))

    def test_remove_product(self):
        HistoryService.add_product(self.user, self.product1)
        HistoryService.remove_product(self.user, self.product1)
        self.assertFalse(HistoryService.is_product_watched(self.user, self.product1))

    def test_is_product_watched(self):
        HistoryViewed.objects.create(user=self.user, product=self.product1)
        self.assertTrue(HistoryService.is_product_watched(self.user, self.product1))
        self.assertFalse(HistoryService.is_product_watched(self.user, self.product2))

    def test_get_history(self):
        HistoryService.add_product(self.user, self.product1)
        HistoryService.add_product(self.user, self.product2)
        history = HistoryService.get_history(self.user)
        self.assertEqual(len(history), 2)

    def test_get_history_count(self):
        self.assertEqual(HistoryService.get_history_count(self.user), 0)
        HistoryService.add_product(self.user, self.product1)
        HistoryService.add_product(self.user, self.product2)
        self.assertEqual(HistoryService.get_history_count(self.user), 2)
