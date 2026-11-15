from django.core.exceptions import ValidationError
from django.test import TestCase
from main.admin import ProductAdminForm
from main.models import Category, Product


class ProductConditionTests(TestCase):
    def setUp(self):
        self.consoles = Category.objects.create(name='Consoles', slug='consoles', category_type='consoles')

    def product(self, **kwargs):
        values = dict(name='Console', slug='console', price='100', category=self.consoles)
        values.update(kwargs)
        return Product(**values)

    def test_unknown_fields_do_not_claim_new_condition_or_stock_firmware(self):
        product = self.product(platform='ps4')
        self.assertEqual(product.condition, '')
        self.assertEqual(product.firmware_status, '')
        self.assertIsNone(product.warranty_months)
        product.save()
        product.refresh_from_db()
        self.assertEqual(product.condition, '')
        self.assertEqual(product.firmware_status, '')

    def test_warranty_only_for_explicit_used_supported_consoles(self):
        for platform, months in [('ps4', 6), ('ps5', 3), ('xbox', 3), ('universal', None), ('', None)]:
            with self.subTest(platform=platform):
                for firmware in ('', 'stock', 'modified'):
                    self.assertEqual(self.product(platform=platform, condition='used', firmware_status=firmware).warranty_months, months)
                for condition in ('', 'new'):
                    self.assertIsNone(self.product(platform=platform, condition=condition).warranty_months)

    def test_accessories_and_disks_do_not_inherit_console_warranty(self):
        for kind in ('accessories', 'subscriptions', 'disks'):
            category = Category.objects.create(name=kind, slug=kind, category_type=kind)
            category.full_clean()
            self.assertIsNone(self.product(category=category, platform='ps4', condition='used').warranty_months)

    def test_invalid_choices_are_rejected(self):
        for field in ('condition', 'firmware_status'):
            with self.subTest(field=field):
                product = self.product(**{field: 'invalid'})
                with self.assertRaises(ValidationError) as error:
                    product.full_clean()
                self.assertIn(field, error.exception.message_dict)

    def test_admin_saves_condition_firmware_and_existing_variant_fields(self):
        form = ProductAdminForm(data={
            'name':'Console', 'slug':'console', 'category':self.consoles.pk, 'price':'100',
            'rating':'5', 'variant_order':'1', 'variant_group':'ps4', 'variant_name':'1 TB',
            'condition':'used', 'firmware_status':'modified', 'platform':'ps4',
        })
        self.assertTrue(form.is_valid(), form.errors)
        product = form.save()
        self.assertEqual(product.warranty_months, 6)
        self.assertEqual(product.firmware_status, 'modified')
        self.assertEqual(product.variant_group, 'ps4')
        self.assertEqual(product.variant_name, '1 TB')
