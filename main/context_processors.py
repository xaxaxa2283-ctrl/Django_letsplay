# main/context_processors.py
from .models import Cart
from django.conf import settings
from .seo import local_business_schema

def cart_counter(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first() if session_key else None

    count = cart.items.count() if cart else 0
    return {'cart_count': count}


def search_metadata(request):
    private = request.path.startswith(("/cart/", "/checkout/", "/order/", "/my-orders/", "/login/", "/register/", "/auth/", "/api/"))
    return {
        "canonical_url": settings.PUBLIC_SITE_URL.rstrip('/') + request.path,
        "private_page": private,
        "local_business_json_ld": "" if private else local_business_schema(),
    }
