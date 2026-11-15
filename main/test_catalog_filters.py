from django.test import TestCase
from main.models import Product, Category

class CatalogStructureTests(TestCase):
    def test_budget_limit_and_malformed_input(self):
        response=self.client.get('/catalog/',{'category':'consoles','max_price':'50'})
        self.assertEqual(response.context['products'],[])
        response=self.client.get('/catalog/',{'category':'consoles','max_price':'100'})
        self.assertEqual(len(response.context['products']),3)
        for invalid in ('NaN','Infinity','-1','0','wrong','100000000000'):
            response=self.client.get('/catalog/',{'category':'consoles','max_price':invalid})
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.context['max_price'],'')

    def test_condition_is_not_applied_to_accessories_or_subscriptions(self):
        for category_type in ('accessories', 'subscriptions'):
            category=Category.objects.create(name=category_type,category_type=category_type)
            Product.objects.create(name=category_type,slug=category_type,price=10,category=category)
            response=self.client.get('/catalog/',{'category':category_type,'condition':'used'})
            self.assertEqual(len(response.context['products']),1)
            self.assertEqual(response.context['active_condition'],'')
            self.assertNotContains(response,'aria-label="Состояние товара"')

    def setUp(self):
        self.category=Category.objects.create(name='Приставки',category_type='consoles')
        for slug,condition,firmware in [('stock-used','used','stock'),('modified-used','used','modified'),('new','new','stock')]:
            Product.objects.create(name=slug,slug=slug,price=100,category=self.category,platform='ps4',condition=condition,firmware_status=firmware,variant_group='ps4-family')

    def test_group_does_not_hide_state_or_firmware(self):
        response=self.client.get('/catalog/',{'category':'consoles','filter':'ps4'})
        self.assertEqual(len(response.context['products']),3)

    def test_combined_filters_and_guarantee(self):
        response=self.client.get('/catalog/',{'category':'consoles','filter':'ps4','condition':'used','firmware':'modified'})
        self.assertEqual([p.slug for p in response.context['products']],['modified-used'])
        self.assertContains(response,'Гарантия 6 мес.')
        detail=self.client.get('/catalog/modified-used/')
        self.assertNotContains(detail,'<div class="sf-setup-box">')
        self.assertContains(detail,'доступность сетевых функций')

    def test_disks_do_not_show_console_bonus(self):
        disks=Category.objects.create(name='Диски',category_type='disks')
        Product.objects.create(name='Test disc',slug='test-disc',price=10,category=disks,platform='ps5',condition='used')
        response=self.client.get('/catalog/',{'category':'disks','filter':'ps5'})
        self.assertEqual([p.slug for p in response.context['products']],['test-disc'])
        detail=self.client.get('/catalog/test-disc/')
        self.assertNotContains(detail,'<div class="sf-setup-box">')
        self.assertNotContains(detail,'Гарантия 3 мес.')
