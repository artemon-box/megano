from shopapp.services.discount import DiscountService

from .services.cart import CartService


def cart_context(request):
    cart_service = CartService()
    cart_items = cart_service.get_cart(request)
    discount = DiscountService()

    total_quantity = 0
    total_price = 0
    price_with_discount = 0
    discounts = []

    if cart_items:
        if isinstance(cart_items[0], dict):
            total_quantity = sum(item["quantity"] for item in cart_items)
            total_price = sum(item["quantity"] * item["product_seller"].price for item in cart_items)
        else:
            total_quantity = sum(item.quantity for item in cart_items)
            total_price = sum(item.quantity * item.product_seller.price for item in cart_items)

        discounts = discount.calculate_discount_price_product(cart_items, total_price)
        if discounts:
            price_with_discount = discounts[0]
            discounts = discounts[1]

    return {
        "total_quantity": total_quantity,
        "total_price": total_price,
        "price_with_discount": price_with_discount,
        "discounts": discounts,
    }
