from random import choice

from django.utils import timezone
from shopapp.models import DailyOfferProduct, ProductSeller


def get_daily_offer():
    today = timezone.now().date()

    daily_offer = DailyOfferProduct.objects.filter(selected_date=today).first()

    if not daily_offer:
        limited_edition_products = ProductSeller.objects.filter(is_limited_edition=True)
        if limited_edition_products:
            selected_product = choice(limited_edition_products)
            daily_offer = DailyOfferProduct(product=selected_product, selected_date=today)
            daily_offer.save()

    return daily_offer.product if daily_offer else None


def get_limited_edition_products():
    today = timezone.now().date()

    daily_offer = DailyOfferProduct.objects.filter(selected_date=today).first()

    limited_edition_products = ProductSeller.objects.filter(is_limited_edition=True)
    if daily_offer:
        limited_edition_products = limited_edition_products.exclude(id=daily_offer.product.id)

    limited_edition_products = limited_edition_products[:16]

    return limited_edition_products
