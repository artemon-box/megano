from django.db.models import Avg
from django.shortcuts import render, get_object_or_404, redirect

from cart_and_orders.services.cart import CartService
from .forms import AddToCartForm, AddReviewForm
from .models import Product, Seller, ProductSeller
from .services.product_review import ProductReviewService
from .utils.details_cache import get_cached_product_by_slug
from .services.recently_viewed import RecentlyViewedService


def product_detail(request, product_slug):
    product = get_cached_product_by_slug(product_slug)
    # reviews = Review.objects.filter(product=product)
    user = request.user
    recently_viewed_service = RecentlyViewedService()
    product_review_service = ProductReviewService()
    cart = CartService()

    # Обработка добавления товара в список последних просмотренных товаров
    if user.is_authenticated:
        recently_viewed_service.add_to_recently_viewed(user_id=user.id, product_slug=product_slug)

    if request.method == 'POST':
        print(request.POST.dict())
        if 'quantity' in request.POST:
            form = AddToCartForm(request.POST)
            if form.is_valid():
                quantity = form.cleaned_data['quantity']
                print(quantity)
                # cart.add_to_cart(user.id, product_slug, quantity)
                return redirect('shopapp:product_detail', product_slug=product_slug)
        elif 'review' in request.POST:
            print('OK')
            form = AddReviewForm(request.POST)
            if form.is_valid():
                print('review_ok')
            #     text = form.cleaned_data['text']
            #     print(text)
            # if user.is_authenticated:
            #     review_text = request.POST.get('review_text', '')
            #     product_review_service.add_review_for_product(product_slug, user, review_text=review_text)
            # else:
            #     pass

    product_sellers = product.productseller_set.all()
    average_price = ProductSeller.objects.aggregate(avg_price=Avg('price'))['avg_price']

    context = {
        'product': product,
        'product_sellers': product_sellers,
        'average_price': average_price,
        # 'reviews_count': ProductReviewService.get_reviews_count(product_id=product_slug),
        # 'reviews': ProductReviewService.get_reviews_for_product(product_id=product_slug),
    }
    return render(request, 'product_detail.jinja2', context)

