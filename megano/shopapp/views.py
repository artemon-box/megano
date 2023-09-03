from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest
from django.shortcuts import render
from django.conf import settings  # Импорт настроек
from django.core.cache import cache
from django.core.paginator import Paginator
from django.views import View
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


def catalog_list(request: HttpRequest):
    filter_form = {}
    if request.method == 'POST':
        price = request.POST.get('price')
        price_from = price.split(';')[0]  # цена от
        price_to = price.split(';')[1]  # цена до
        title = request.POST.get('title')  # название товара
        available = request.POST.get('available')  # товар в наличии

        qs = Product.objects.all().filter(price__gte=price_from).filter(price__lte=price_to)
        if title:
            qs = qs.filter(name__icontains=title)
        if available:
            qs = qs.filter(available=True)

        filter_form['price'] = price
        filter_form['available'] = available
        filter_form['title'] = title

        cache.set('qs', qs, 360)
        cache.set('filter_form', filter_form, 360)
    if cache.get('qs'):
        qs = cache.get('qs')
    else:
        qs = Product.objects.all()
    if request.GET.get('sort'):
        qs = qs.order_by(request.GET.get('sort'))
        cache.set('qs', qs, 360)
    filter_form = cache.get('filter_form')

    # Пагинация
    paginator = Paginator(qs, 10)  # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'products': page_obj,
        'filter_form': filter_form
    }
    return render(request, 'catalog.jinja2', context=context)


class AddToComparison(View):
    """
    добавить товар в список сравниваемых товаров
    """

    def get(self, request, **kwargs):
        compare_list = ComparedProductsService(request)
        product = get_object_or_404(Product, id=kwargs['product_id'])
        compare_list.add_to_compared_products(product)
        return redirect(request.META.get('HTTP_REFERER'))


class RemoveFromComparison(View):
    """
    удалить товар из списка сравниваемых товаров
    """

    def get(self, request, **kwargs):
        compare_list = ComparedProductsService(request)
        product = get_object_or_404(Product, id=kwargs['product_id'])
        if product in compare_list:
            compare_list.remove_from_compared_products(product)
        return redirect('shopapp:compare_list')


class ComparisonOfProducts(View):
    """
    вывести список сравниваемых товаров
    """
    temlate_name = 'shopapp/comparison.jinja2'

    def get(self, request):
        compare_list = ComparedProductsService(request)
        return render(
            request,
            self.temlate_name,
            {
                'title': 'тут будет сравнение товаров',
                # 'compare_list': compare_list,
            }
        )
