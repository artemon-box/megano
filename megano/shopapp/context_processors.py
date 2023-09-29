from shopapp.utils.banners_cache import get_random_active_product_banners
from shopapp.utils.categories_cache import get_cached_active_categories

from .services.compared_products import ComparedProductsService


def categories_menu(request):
    """
    Функция для получения и возвращения в общий контекст активных категорий
    """
    active_categories = get_cached_active_categories()

    context = {
        "active_categories": active_categories,
    }

    return context


def random_product_banners(request):
    """
    Функция для получения и возвращения в общий контекст трёх случайных баннеров
    """
    random_banners = get_random_active_product_banners()

    context = {
        "random_banners": random_banners,
        "banner_indices": [1, 2, 3],
    }

    return context


def compare_list(request):
    return {"compare_list": ComparedProductsService(request)}
