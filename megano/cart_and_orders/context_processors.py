from .services.cart import CartService


def cart_context(request):
    user_id = request.user.id if request.user.is_authenticated else None

    total_quantity = 0
    total_price = 0

    if user_id:
        cart_service = CartService()
        cart_items = cart_service.get_cart(user_id=user_id)

        total_quantity = sum(item.quantity for item in cart_items)
        total_price = sum(item.quantity * item.product_seller.price for item in cart_items)

    return {'total_quantity': total_quantity, 'total_price': total_price}
