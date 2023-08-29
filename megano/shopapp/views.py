from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings  # Импорт настроек
from django.core.cache import cache
from .models import Category, Product
from .services.compared_products import ComparedProductsService


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


def add_to_comparison(request, product_id):
    """
    добавить товар в список сравниваемых товаров
    """
    compare_list = ComparedProductsService(request)
    product = get_object_or_404(Product, id=product_id)
    compare_list.add_to_compared_products(product)
    return redirect(request.META.get('HTTP_REFERER'))


def remove_from_comparison(request, product_id):
    """
    удалить товар из списка сравниваемых товаров
    """
    compare_list = ComparedProductsService(request)
    product = get_object_or_404(Product, id=product_id)
    if product in compare_list:
        compare_list.remove_from_compared_products(product)
    return redirect('shopapp:compare_list')


def comparison_of_products(request):
    """
    вывести список сравниваемых товаров
    """
    compare_list = ComparedProductsService(request)
    return render(
        request,
        'shopapp/comparison.jinja2',
        {
            'title': 'тут будет сравнение товаров',
            'compare_list': compare_list
        }
    )
