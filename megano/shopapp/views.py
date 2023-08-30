from django.shortcuts import render
from django.conf import settings  # Импорт настроек
from django.core.cache import cache
from .models import Category


def category_menu_view(request):
    # Получение активных категорий и сортировка по индексу сортировки
    active_categories = Category.objects.filter(is_active=True).order_by('sort_index')

    # Кэширование данных на указанное время
    cache_key = 'category_menu'
    cache_timeout = getattr(settings, 'CATEGORY_MENU_CACHE_TIMEOUT', 86400)  # Получение параметра из настроек
    cached_menu = cache.get(cache_key)
    if cached_menu is None:
        cache.set(cache_key, active_categories, cache_timeout)
        cached_menu = active_categories

    # Возвращение данных в шаблон
    return render(request, 'category_menu.jinja2', {'active_categories': cached_menu})


def test_base_template(request):
    return render(request, 'base.jinja2', {})


def test_registr_template(request):
    return render(request, 'registr.jinja2', {})
