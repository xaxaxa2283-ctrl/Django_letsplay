from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from main.models import Product
from django.conf import settings
from types import SimpleNamespace
from urllib.parse import urlsplit

class PublicSitemap(Sitemap):
    protocol = 'https'

    def get_urls(self, page=1, site=None, protocol=None):
        origin = urlsplit(settings.PUBLIC_SITE_URL)
        return super().get_urls(page=page, site=SimpleNamespace(domain=origin.netloc), protocol=origin.scheme)


class StaticViewSitemap(PublicSitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ['main:home', 'main:about', 'main:catalog', 'main:reviews', 'main:service_setup', 'main:service_console_selection', 'main:delivery', 'main:warranty']

    def location(self, item):
        return reverse(item)

class ProductSitemap(PublicSitemap):
    priority = 0.9
    changefreq = "daily"

    def items(self):
        return Product.objects.filter(is_active=True).exclude(slug__isnull=True).exclude(slug='')

    def lastmod(self, obj):
        return obj.updated_at
