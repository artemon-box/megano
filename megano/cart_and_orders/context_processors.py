from .services.cart import CartService


def cart_context(request):
    cart_service = CartService()
    cart_items = cart_service.get_cart(request)

    total_quantity = 0
    total_price = 0

    if cart_items:
        if isinstance(cart_items[0], dict):
            total_quantity = sum(item["quantity"] for item in cart_items)
            total_price = sum(item["quantity"] * item["product_seller"].price for item in cart_items)
        else:
            total_quantity = sum(item.quantity for item in cart_items)
            total_price = sum(item.quantity * item.product_seller.price for item in cart_items)

    return {"total_quantity": total_quantity, "total_price": total_price}
