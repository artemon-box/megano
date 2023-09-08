from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.core.cache import cache
from .models import ProductReview
from django.core.paginator import Paginator
from django.db.models import Avg

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
            'product_reviews': product_reviews,
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
    # qs = [{'1': {'name': 1}}, {'2': {'name': 2}}, {'3': {'name': 3}}, {'4': {'name': 4}}]
    qs = []
    if request.method == 'POST':
        price = request.POST.get('price')
        price_from = price.split(';')[0]  # цена от
        price_to = price.split(';')[1]  # цена до
        title = request.POST.get('title')  # название товара
        available = request.POST.get('available')  # товар в наличии
        qs = Product.objects.all().filter(price__gte=int(price_from)).filter(price__lte=int(price_to))

        if qs and title:
            qs = qs.filter(name__icontains=title)
        if qs and available:
            qs = qs.filter(archived=False)
        if qs:
            cache.set('qs', qs, 360)
        else:
            qs = []
            cache.set('qs', qs, 360)
    if cache.get('qs'):
        qs = cache.get('qs')
    if request.GET.get('sort') and qs:
        if request.GET.get('sort') == 'review':
            qs = sorted(qs, key=lambda a: a.get_reviews_count)
        elif request.GET.get('sort') == '-review':
            qs = sorted(qs, key=lambda a: a.get_reviews_count, reverse=True)
        else:
            qs = qs.order_by(request.GET.get('sort'))
            cache.set('qs', qs, 360)

    # Пагинация
    paginator = Paginator(qs, 4)  # Show 10 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'products': page_obj,
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
