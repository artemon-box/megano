from django.conf import settings
from django.core.cache import cache
from shopapp.models import ProductSeller


def get_cached_top_products():
    # ключ хэша
    cache_key = "top_products"
    # попытка получить данные кэша
    cached_top_products = cache.get(cache_key)

    # Если данные кэша отсутствуют, выполнить запрос к БД
    if cached_top_products is None:
        # Получение топ-товаров, сначала по количеству просмотров, затем по количеству покупок
        top_products = ProductSeller.objects.all()[:8]

        # Кэширование данных на указанное время
        cache_timeout = getattr(settings, "TOP_PRODUCTS_CACHE_TIMEOUT")
        cache.set(cache_key, top_products, cache_timeout)
        cached_top_products = top_products
    return cached_top_products
