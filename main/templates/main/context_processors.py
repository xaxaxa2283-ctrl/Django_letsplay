from main.models import Cart, CartItem

def cart_count(request):
    cart_items = 0
    cart_id = request.session.get('cart_id')
    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id)
            cart_items = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            pass
    return {'cart_count': cart_items}
