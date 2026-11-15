from django.test import Client, TestCase
from django.urls import reverse
from main.models import Category, Product, Review
from main.services.reviews_stats import invalidate_reviews_stats_cache


class StorefrontIntegrationTests(TestCase):
    def setUp(self):
        invalidate_reviews_stats_cache()
        category = Category.objects.create(name='Приставки', category_type='consoles', slug='consoles')
        self.product = Product.objects.create(name='Test PS5', slug='test-ps5', price='12345', category=category, platform='ps5')

    def test_public_pages_render_one_canonical_and_local_assets(self):
        for route in ('main:home', 'main:catalog', 'main:reviews', 'main:about', 'main:service_setup'):
            response=self.client.get(reverse(route))
            self.assertEqual(response.status_code,200)
            self.assertContains(response,'rel="canonical"',count=1)
            self.assertContains(response,'/static/css/storefront.css',count=1)
            if route == 'main:home':
                self.assertContains(response, 'Месяц PS Plus в подарок')
                self.assertContains(response, 'Доступ к каталогу до 700 игр')
            self.assertNotContains(response, '700+ игр')

    def test_home_uses_database_products(self):
        response=self.client.get(reverse('main:home'))
        self.assertContains(response,'Test PS5')
        self.assertContains(response,'12345')

    def test_reviews_label_counts_and_exclude_generated(self):
        Review.objects.create(name='Настоящий',text='Опыт покупки',is_approved=True)
        Review.objects.create(name='Generated',text='Never show this',is_approved=True,is_generated=True)
        response=self.client.get(reverse('main:reviews'))
        self.assertContains(response,'На нашем сайте · 1 отзыв')
        self.assertNotContains(response,'Never show this')
        self.assertNotContains(response,'99%')
        self.assertNotContains(response,'1900')

    def test_crawlers_find_correct_product_url(self):
        response=self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'/catalog/test-ps5/')
        self.assertNotContains(response,'/catalog/product/')
        self.assertContains(self.client.get('/robots.txt'),'Sitemap: https://letsplayekb.shop/sitemap.xml')

    def test_hidden_product_and_forged_cart_request_are_rejected(self):
        strict_client=Client(enforce_csrf_checks=True)
        self.assertEqual(strict_client.post(reverse('main:add_to_cart', args=[self.product.pk])).status_code,403)
        self.product.is_active=False
        self.product.save()
        self.assertEqual(self.client.get(self.product.get_absolute_url()).status_code,404)
        self.assertEqual(self.client.post(reverse('main:add_to_cart', args=[self.product.pk])).status_code,404)

    def test_product_schema_is_safe_and_does_not_invent_specifications(self):
        self.product.description='</script><script>alert(1)</script>'
        self.product.save()
        response=self.client.get(self.product.get_absolute_url())
        self.assertContains(response,'application/ld+json')
        self.assertNotContains(response,'</script><script>alert(1)</script>')
        self.assertNotContains(response,'NewCondition')
        self.assertNotContains(response,'Япония')

    def test_preparation_is_not_promised_for_xbox_or_modified_ps4(self):
        self.assertContains(self.client.get(self.product.get_absolute_url()), 'Приставка с подготовкой')
        xbox = Product.objects.create(name='Test Xbox', slug='test-xbox', price='20000', category=self.product.category, platform='xbox')
        modified_ps4 = Product.objects.create(name='Test modified PS4', slug='test-modified-ps4', price='18000', category=self.product.category, platform='ps4', firmware_status='modified')
        for product in (xbox, modified_ps4):
            response = self.client.get(product.get_absolute_url())
            self.assertContains(response, 'Цена приставки')
            self.assertNotContains(response, 'Приставка с подготовкой')
            self.assertNotContains(response, 'Под ключ — входит в покупку')

    def test_delivery_page_has_no_unconfirmed_rates_or_free_delivery(self):
        response = self.client.get(reverse('main:delivery'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Стоимость, срок и способ доставки согласуем до оформления заказа')
        self.assertNotContains(response, '500-800')
        self.assertNotContains(response, '800–1500')
        self.assertNotContains(response, 'Бесплатная доставка')
