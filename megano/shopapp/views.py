from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.core.cache import cache
from .models import ProductReview
from django.core.paginator import Paginator
from django.db.models import Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from cart_and_orders.services.cart import CartService
from .forms import AddToCartForm, ProductReviewForm
from .models import ProductSeller
from .services.discount import DiscountService
from .services.product_review import ProductReviewService
from .utils.details_cache import get_cached_product_by_slug
from .services.recently_viewed import RecentlyViewedService

from django.shortcuts import render, redirect

from django.views import View
from .models import Product
from .services.compared_products import ComparedProductsService


class ProductDetailView(View):
    """
    DetailView для детальной страницы товара
    """
    template_name = 'product_detail.jinja2'
    model = Product

    review_service = ProductReviewService()
    discount_service = DiscountService()
    recently_viewed_service = RecentlyViewedService()
    cart = CartService()

    def get(self, request, product_slug):
        product = get_cached_product_by_slug(product_slug)

        try:
            product_reviews = self.review_service.get_reviews_for_product(product)
        except ProductReview.DoesNotExist:
            product_reviews = []

        # Определите количество элементов на странице
        items_per_page = 3  # Например, 10 отзывов на странице

        # Создайте объект Paginator
        paginator = Paginator(product_reviews, items_per_page)

        # Получите номер страницы из параметров GET-запроса (если не указан, используйте 1)
        page_number = request.GET.get('page')
        print(page_number)
        page_obj = paginator.get_page(page_number)
        print(page_obj)

        extra_images = product.extra_images.all()
        user = request.user
        tags = product.category.tags.all().union(product.tags.all())
        reviews_count = self.review_service.get_reviews_count(product=product)

        product_sellers = product.productseller_set.all()
        average_price = ProductSeller.objects.aggregate(avg_price=Avg('price'))['avg_price']
        # average_price_discount = self.discount_service.calculate_discount_price_product(product)

        if user.is_authenticated:
            self.recently_viewed_service.add_to_recently_viewed(user_id=user.id, product_slug=product_slug)

        context = {
            'extra_images': extra_images,
            'product': product,
            'product_sellers': product_sellers,
            'average_price': average_price,
            'tags': tags,
            'product_reviews': page_obj,
            'reviews_count': reviews_count
        }
        return render(request, self.template_name, context)

    def post(self, request, product_slug):
        product = get_cached_product_by_slug(product_slug)
        user = request.user

        if 'quantity' in request.POST:
            form = AddToCartForm(request.POST)
            if form.is_valid():
                quantity = form.cleaned_data['quantity']
                # self.cart.add_to_cart(user.id, product_slug, quantity)
                return redirect('shopapp:product_detail', product_slug=product_slug)

        elif 'review_text' in request.POST:
            review_form = ProductReviewForm(request.POST)
            if review_form.is_valid():
                review_text = review_form.cleaned_data['review_text']
                print(type(review_text))
                self.review_service.add_review_for_product(product=product, user_id=user.id, review_text=review_text)

        return redirect('shopapp:product_detail', product_slug=product_slug)


def index(request):
    return render(request, 'index.jinja2')


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
        compare_list.add_to_compared_products(kwargs['product_id'])
        return redirect(request.META.get('HTTP_REFERER'))


class RemoveFromComparison(View):
    """
    удалить товар из списка сравниваемых товаров
    """

    def get(self, request, **kwargs):
        compare_list = ComparedProductsService(request)
        compare_list.remove_from_compared_products(kwargs['product_id'])
        return redirect('shopapp:compare_list')


class ComparisonOfProducts(View):
    """
    вывести список сравниваемых товаров
    """
    temlate_name = 'shopapp/comparison.jinja2'

    def get(self, request):
        compare_list = ComparedProductsService(request)
        compare_list = compare_list.get_compared_products()
        compared_products = [get_object_or_404(Product, id=product_id) for product_id in compare_list]
        return render(
            request,
            self.temlate_name,
            {
                'compared_products': compared_products,
            }
        )
