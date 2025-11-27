from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from main.models import Product

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ['letsplay:home', 'letsplay:about', 'letsplay:catalog', 'letsplay:reviews']

    def location(self, item):
        return reverse(item)

class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = "daily"

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at
