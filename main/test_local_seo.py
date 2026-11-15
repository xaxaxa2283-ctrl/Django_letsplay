import json
import re
from django.test import TestCase, override_settings
from main.seo import local_business_schema


class LocalSeoTests(TestCase):
    def test_store_schema_uses_confirmed_contact_details_only(self):
        data = json.loads(local_business_schema())
        self.assertEqual(data['@type'], 'Store')
        self.assertEqual(data['address']['addressLocality'], 'Екатеринбург')
        self.assertEqual(data['address']['streetAddress'], 'ул. Луначарского, 134')
        self.assertEqual(data['hasMap'], 'https://yandex.ru/maps/org/letsplay/199283418342/')
        for unverified in ('aggregateRating', 'review', 'openingHours', 'openingHoursSpecification', 'priceRange', 'sameAs'):
            self.assertNotIn(unverified, data)

    @override_settings(PUBLIC_SITE_URL='https://new-shop.example/', LEGAL_TRADE_NAME='</script><script>bad</script>')
    def test_schema_safe_serialization_and_configurable_origin(self):
        text = local_business_schema()
        self.assertNotIn('</script>', text)
        data = json.loads(text)
        self.assertEqual(data['url'], 'https://new-shop.example/')
        self.assertEqual(data['@id'], 'https://new-shop.example/#store')
        self.assertTrue(data['image'].startswith('https://new-shop.example/'))
        self.assertContains(self.client.get('/robots.txt'), 'Sitemap: https://new-shop.example/sitemap.xml')

    def test_both_base_templates_render_single_store_schema(self):
        for path in ('/', '/about/', '/catalog/'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S)
            stores = [json.loads(block) for block in blocks if json.loads(block).get('@type') == 'Store']
            self.assertEqual(len(stores), 1)
        self.assertNotContains(self.client.get('/cart/'), '"@type": "Store"')
