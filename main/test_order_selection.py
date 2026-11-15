from django.test import TestCase
from django.urls import reverse
from main.models import Cart, CartItem, Category, OrderItem, Product, Order


class OrderSelectionSnapshotTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Consoles', category_type='consoles')
        self.product = Product.objects.create(name='PS4 Slim', slug='ps4-slim', category=self.category,
            price='21000', platform='ps4', condition='used', firmware_status='modified', variant_name='1 TB')

    def test_checkout_preserves_configuration_after_product_changes_and_deletion(self):
        session = self.client.session
        cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(cart=cart, product=self.product)
        response = self.client.post(reverse('main:checkout'), {'name':'Buyer', 'phone':'123456789',
            'personal_data_consent':'yes', 'delivery_method':'pickup', 'payment_method':'cash'})
        self.assertEqual(response.status_code, 302)
        item = OrderItem.objects.get()
        expected = '1 TB · Б/у · Прошивка: Модифицированная · Гарантия: 6 мес.'
        self.assertEqual(item.selection_summary, expected)
        self.product.variant_name = '500 GB'
        self.product.condition = 'new'
        self.product.firmware_status = 'stock'
        self.product.save()
        item.refresh_from_db()
        self.assertEqual(item.selection_summary, expected)
        self.product.delete()
        item.refresh_from_db()
        self.assertIsNone(item.product_id)
        self.assertEqual(item.selection_summary, expected)
        self.assertEqual(item.product_name, 'PS4 Slim')

    def test_unknown_and_other_platform_firmware_not_claimed(self):
        self.product.platform = 'ps5'
        self.product.condition = ''
        self.product.variant_name = ''
        self.assertEqual(self.product.get_selection_summary(), '')
        self.product.platform = 'ps4'
        self.category.category_type = 'accessories'
        self.assertEqual(self.product.get_selection_summary(), '')

    def test_variant_already_in_title_is_not_repeated_and_length_is_bounded(self):
        self.product.name = 'PS4 Slim 1 TB'
        self.assertNotIn('1 TB', self.product.get_selection_summary())
        self.product.variant_name = 'X' * 400
        self.assertLessEqual(len(self.product.get_selection_summary()), 300)

    def test_legacy_order_item_defaults_to_empty_snapshot(self):
        order = Order.objects.create(customer_name='Buyer', customer_email='', customer_phone='123',
            delivery_method='pickup', payment_method='cash', total_price='100')
        item = OrderItem.objects.create(order=order, product=self.product, product_name='Old title',
            product_price='100', quantity=1)
        self.assertEqual(item.selection_summary, '')
