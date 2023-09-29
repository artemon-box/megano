from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Category, Product, ProductSeller


@receiver([post_save, post_delete], sender=Category)
def update_category_active(sender, instance, **kwargs):
    cache_key = 'active_categories'
    cache.delete(cache_key)


@receiver([post_save, post_delete], sender=Product)
def clear_banner_cache(sender, instance, **kwargs):
    cache_key = 'banners_cache'
    cache.delete(cache_key)


@receiver(post_save, sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    cache_key = f'product_{instance.slug}'
    cache.delete(cache_key)


@receiver([post_save, post_delete], sender=ProductSeller)
def clear_top_products_cache(sender, instance, **kwargs):
    cache_key = 'top_products'
    cache.delete(cache_key)
