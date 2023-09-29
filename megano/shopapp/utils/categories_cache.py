from django.conf import settings
from django.core.cache import cache
from shopapp.models import Category


def get_cached_active_categories():
    # Ключ для кэша
    cache_key = 'active_categories'

    # Попытка получить данные из кэша
    cached_categories = cache.get(cache_key)

    # Если данные отсутствуют в кэше, выполнить запрос к базе данных
    if cached_categories is None:
        # Получение активных категорий и сортировка по индексу сортировки
        active_categories = Category.objects.filter(products__available=True).distinct()

        # Кэширование данных на указанное время
        cache_timeout = getattr(settings, 'CATEGORY_MENU_CACHE_TIMEOUT', 86400)
        cache.set(cache_key, active_categories, cache_timeout)

        cached_categories = active_categories

    return cached_categories
