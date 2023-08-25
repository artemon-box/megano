from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Category, Product
from django.core.cache import cache


@receiver(pre_save, sender=Category)
def update_category_active(sender, instance, **kwargs):
    if instance.products.filter(active=True).exists():
        instance.active = True


@receiver([post_save, post_delete], sender=Product)
def clear_banner_cache(sender, instance, **kwargs):
    cache_key = 'banners_cache'
    cache.delete(cache_key)
