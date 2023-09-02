from django.db.models import Avg

from cart_and_orders.services.cart import CartService
from .forms import AddToCartForm, AddReviewForm
from .models import Product, Seller, ProductSeller
from .services.discount import DiscountService
from .services.product_review import ProductReviewService
from .utils.details_cache import get_cached_product_by_slug
from .services.recently_viewed import RecentlyViewedService

from django.shortcuts import render, redirect
from django.views import View
from .models import Product


class ProductDetailView(View):
    template_name = 'product_detail.jinja2'
    model = Product

    def get(self, request, product_slug):
        recently_viewed_service = RecentlyViewedService()
        discount_service = DiscountService()

        product = get_cached_product_by_slug(product_slug)
        user = request.user

        product_sellers = product.productseller_set.all()
        average_price = ProductSeller.objects.aggregate(avg_price=Avg('price'))['avg_price']
        average_price_discount = discount_service.calculate_discount_price_product(product)

        if user.is_authenticated:
            recently_viewed_service.add_to_recently_viewed(user_id=user.id, product_slug=product_slug)

        context = {
            'product': product,
            'product_sellers': product_sellers,
            'average_price': average_price_discount,
        }
        return render(request, self.template_name, context)

    def post(self, request, product_slug):
        cart = CartService()
        review_service = ProductReviewService()
        product = get_cached_product_by_slug(product_slug)
        user = request.user

        if 'quantity' in request.POST:
            form = AddToCartForm(request.POST)
            if form.is_valid():
                quantity = form.cleaned_data['quantity']
                # cart.add_to_cart(user.id, product_slug, quantity)
                return redirect('shopapp:product_detail', product_slug=product_slug)

        elif 'review_text' in request.POST:
            form = AddReviewForm(request.POST)
            if form.is_valid():
                review_text = form.cleaned_data['review_text']
                # review_service.add_review_for_product(product_slug, user.id, review_text)

        return redirect('shopapp:product_detail', product_slug=product_slug)


def index(request):
    return render(request, 'index.jinja2')
