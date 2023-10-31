from typing import List

from django.utils import timezone
from histviewapp.models import HistoryViewed
from shopapp.models import Product


class HistoryService:
    @staticmethod
    def add_product(user, product: Product) -> None:
        history, created = HistoryViewed.objects.update_or_create(
            user=user, product=product, defaults={"watched_at": timezone.now()}
        )

    @staticmethod
    def remove_product(user, product: Product) -> None:
        HistoryViewed.objects.filter(user=user, product=product).delete()

    @staticmethod
    def is_product_watched(user, product: Product) -> bool:
        return HistoryViewed.objects.filter(user=user, product=product).exists()

    @staticmethod
    def get_history(user, count: int = 20) -> List[Product]:
        history_qs = HistoryViewed.objects.filter(user=user)[:count]
        return history_qs

    @staticmethod
    def get_history_count(user) -> int:
        return HistoryViewed.objects.filter(user=user).count()
