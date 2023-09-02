import random
from django.core.cache import cache
from django.conf import settings
from megano.shopapp.models import Product


def get_random_active_product_banners():
    # Ключ для кэша
    cache_key = 'random_product_banners'

    # Попытка получить данные из кэша
    cached_banners = cache.get(cache_key)

    # Если данные отсутствуют в кэше, выполнить запрос к базе данных
    if cached_banners is None:
        # Получение случайных активных товаров (предполагая, что у товаров есть поле is_active)
        active_products = Product.objects.filter(is_active=True)

        # Получение трех случайных товаров из активных товаров
        random_products = random.sample(list(active_products), 3)

        # Создание списка баннеров на основе случайных товаров
        banners = []
        for product in random_products:
            banner = {
                'title': product.name,
                'text': f"Get the {product.name} with great discount!",
                'image_url': product.image.url,  # Заменить на соответствующее поле из модели Product
            }
            banners.append(banner)

        # Кэширование данных на указанное время
        cache_timeout = getattr(settings, 'PRODUCT_BANNER_CACHE_TIMEOUT', 600)  # 10 минут (в секундах)
        cache.set(cache_key, banners, cache_timeout)

        cached_banners = banners

    return cached_banners
