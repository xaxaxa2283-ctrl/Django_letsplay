from django.http import HttpResponse
from django.conf import settings
from urllib.parse import urljoin
import json
from django.templatetags.static import static


def product_schema(product):
    url = settings.PUBLIC_SITE_URL.rstrip('/') + product.get_absolute_url()
    data = {
        '@context': 'https://schema.org', '@type': 'Product',
        'name': product.name, 'url': url,
        'offers': {'@type': 'Offer', 'url': url, 'priceCurrency': 'RUB',
                   'price': str(product.price),
                   'availability': 'https://schema.org/' + ('InStock' if product.in_stock else 'OutOfStock')},
    }
    if product.get_image_url():
        data['image'] = urljoin(settings.PUBLIC_SITE_URL, product.get_image_url())
    if product.description:
        data['description'] = product.description
    return json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def local_business_schema():
    """Public store details confirmed by the contact pages, without inferred claims."""
    origin = settings.PUBLIC_SITE_URL.rstrip('/')
    data = {
        '@context': 'https://schema.org',
        '@type': 'Store',
        '@id': origin + '/#store',
        'name': settings.LEGAL_TRADE_NAME,
        'url': origin + '/',
        'telephone': settings.LEGAL_CONTACT_PHONE,
        'email': settings.LEGAL_CONTACT_EMAIL,
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': 'ул. Луначарского, 134',
            'addressLocality': 'Екатеринбург',
            'addressRegion': 'Свердловская область',
            'addressCountry': 'RU',
        },
        'image': urljoin(origin + '/', static('images/about_us.jpg')),
        'hasMap': 'https://yandex.ru/maps/org/letsplay/199283418342/',
    }
    return json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def robots(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /admin/\nDisallow: /cart/\n"
        "Disallow: /checkout/\nDisallow: /order/\nDisallow: /my-orders/\n"
        "Disallow: /api/\nDisallow: /login/\nDisallow: /register/\nDisallow: /auth/\n"
        f"Sitemap: {settings.PUBLIC_SITE_URL.rstrip('/')}/sitemap.xml\n",
        content_type="text/plain; charset=utf-8",
    )
