import random

from django.conf import settings
from django.core.cache import cache
from shopapp.models import Product


def get_random_active_product_banners():
    # Ключ для кэша
    cache_key = "random_product_banners"

    # Попытка получить данные из кэша
    cached_banners = cache.get(cache_key)

    # Если данные отсутствуют в кэше, выполнить запрос к базе данных
    if cached_banners is None:
        # Получение случайных активных товаров (предполагая, что у товаров есть поле is_active)
        active_products = Product.objects.filter(available=True)

        # Получение трех случайных товаров из активных товаров
        try:
            if len(active_products) >= 3:
                banners = random.sample(list(active_products), 3)
            else:
                banners = list(active_products)
        except ValueError:
            banners = []

        cache_timeout = getattr(settings, "PRODUCT_BANNER_CACHE_TIMEOUT", 600)  # 10 минут (в секундах)
        cache.set(cache_key, banners, cache_timeout)

        cached_banners = banners

    return cached_banners
