from .models import Category
from shopapp.utils.banners import get_random_active_product_banners
from .services.compared_products import ComparedProductsService


def categories_menu(request):
    active_categories = Category.objects.all()
    return {'categories_menu': active_categories}


def random_product_banners(request):
    # Получаем случайные активные продукты для баннеров
    random_banners = get_random_active_product_banners()

    # Добавляем продукты в контекст
    context = {
        'random_banners': random_banners,
    }

    return context


def compare_list(request):
    return {'compare_list': ComparedProductsService(request)}
