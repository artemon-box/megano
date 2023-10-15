import random

from shopapp.models import ProductSeller


def get_limited_edition_products():
    # Получение товаров из ограниченного тиража
    limited_edition_products = ProductSeller.objects.filter(is_limited_edition=True)[:16]
    return limited_edition_products


def get_limited_offers():
    # Получение товара ограниченного предложения
    limited_offers_products = get_limited_edition_products()
    if limited_offers_products:
        return random.choice(limited_offers_products)
    else:
        return None
