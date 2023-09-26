from typing import List
from django.utils import timezone
from shopapp.models import ProductSeller
from histviewapp.models import HistoryViewed
from django.conf import settings


class HistoryService:
    @staticmethod
    def add_product(user: settings.AUTH_USER_MODEL, product: ProductSeller) -> None:
        history_qs = HistoryViewed.objects.filter(user=user, product=product)

        if not history_qs.exists():
            HistoryViewed.objects.create(user=user, product=product)
        else:
            history = history_qs.first()
            history.watched_at = timezone.now()
            history.save()

    @staticmethod
    def remove_product(user: settings.AUTH_USER_MODEL, product: ProductSeller) -> None:
        HistoryViewed.objects.filter(user=user, product=product).delete()

    @staticmethod
    def is_product_watched(user: settings.AUTH_USER_MODEL, product: ProductSeller) -> bool:
        return HistoryViewed.objects.filter(user=user, product=product).exists()

    @staticmethod
    def get_history(user: settings.AUTH_USER_MODEL, count: int = 20) -> List[ProductSeller]:
        history_qs = HistoryViewed.objects.filter(user=user)[:count]
        return [product_s.product for product_s in history_qs]

    @staticmethod
    def get_history_count(user: settings.AUTH_USER_MODEL) -> int:
        return HistoryViewed.objects.filter(user=user).count()
