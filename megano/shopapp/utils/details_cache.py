from django.core.cache import cache
from django.conf import settings
from shopapp.models import Product


def get_cached_product_by_slug(product_slug):
    cache_key = f'product_{product_slug}'

    cached_product = cache.get(cache_key)

    if cached_product is None:
        product = Product.objects.get(slug=product_slug)

        cache_timeout = getattr(settings, 'PRODUCT_CACHE_TIMEOUT', 86400)  # 24 hours
        cache.set(cache_key, product, cache_timeout)

        cached_product = product

        print('------Successfully cached details')

    return cached_product
