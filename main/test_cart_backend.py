from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.models import Category, Product, Cart, CartItem, Order, OrderItem


class CartBackendTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Console', slug='console', price='150',
            category=Category.objects.create(name='Consoles', category_type='consoles'))
        session = self.client.session
        self.cart = Cart.objects.create(session_key=session.session_key)
        self.item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.url = reverse('main:update_cart_item', args=[self.item.pk])

    def update(self, body):
        return self.client.post(self.url, body, content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def test_malformed_updates_are_400_and_keep_cart_unchanged(self):
        for body in ('[]', 'null', '{}', '{', '{"delta":"bad"}', '{"delta":true}', '{"delta":1.5}', '{"delta":1000000000000}'):
            with self.subTest(body=body):
                self.assertEqual(self.update(body).status_code, 400)
                self.item.refresh_from_db()
                self.assertEqual(self.item.quantity, 2)

    def test_unavailable_product_cannot_increase_but_can_be_removed(self):
        self.product.in_stock = False
        self.product.save()
        self.assertEqual(self.update('{"delta":1}').status_code, 409)
        self.assertEqual(self.update('{"delta":-1}').json()['quantity'], 1)
        self.assertEqual(self.update('{"delta":-1}').json()['quantity'], 0)
        self.assertFalse(CartItem.objects.filter(pk=self.item.pk).exists())

    def test_zero_price_product_cannot_be_added_or_increased(self):
        self.product.price = 0
        self.product.save()
        self.assertFalse(self.product.is_purchasable)
        self.assertEqual(self.update('{"delta":1}').status_code, 409)
        response = self.client.post(reverse('main:add_to_cart', args=[self.product.pk]))
        self.assertEqual(response.status_code, 404)

    def test_other_session_cannot_modify_item(self):
        from django.test import Client
        response = Client().post(self.url, {'action':'increase'})
        self.assertEqual(response.status_code, 404)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 2)

    def test_checkout_rejects_changed_availability_and_preserves_cart(self):
        self.product.is_active = False
        self.product.save()
        response = self.client.post(reverse('main:checkout'), {
            'name':'Buyer', 'phone':'+79991234567', 'personal_data_consent':'yes',
            'delivery_method':'pickup', 'payment_method':'cash'})
        self.assertRedirects(response, reverse('main:cart_view'))
        self.assertFalse(Order.objects.exists())
        self.assertTrue(self.cart.items.exists())


class OrderAdminTests(TestCase):
    def test_order_with_items_can_be_opened_by_staff(self):
        user = get_user_model().objects.create_superuser(username='staff', email='staff@example.com', password='test-only')
        self.client.force_login(user)
        order = Order.objects.create(customer_name='Buyer', customer_email='', customer_phone='123',
            delivery_method='pickup', payment_method='cash', total_price='300')
        OrderItem.objects.create(order=order, product_name='Console', product_price='150', quantity=2)
        response = self.client.get(reverse('admin:main_order_change', args=[order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Console')
        item = order.items.get()
        response = self.client.post(reverse('admin:main_order_change', args=[order.pk]), {
            'customer_name': 'Buyer updated', 'customer_email': '', 'customer_phone': '123',
            'delivery_method': 'pickup', 'payment_method': 'cash', 'status': 'confirmed',
            'items-TOTAL_FORMS': '1', 'items-INITIAL_FORMS': '1',
            'items-MIN_NUM_FORMS': '0', 'items-MAX_NUM_FORMS': '0',
            'items-0-id': str(item.pk), 'items-0-order': str(order.pk), '_save': 'Save',
        })
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        item.refresh_from_db()
        self.assertEqual(order.status, 'confirmed')
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.product_price, 150)

class ProductAdminFormTests(TestCase):
    @override_settings(PUBLIC_SITE_URL='https://new-shop.example/')
    def test_local_recovery_image_can_be_saved_with_edited_price(self):
        from main.admin import ProductAdminForm
        category = Category.objects.create(name='Console', category_type='consoles')
        product = Product.objects.create(name='Console', slug='recovered-console', category=category,
            price='150', image_url='/static/recovered-catalog/1.jpg')
        data = {'name':product.name, 'slug':product.slug, 'category':category.pk, 'price':'175',
            'image_url':product.image_url, 'rating':'5', 'variant_order':'0', 'is_active':'on', 'in_stock':'on'}
        form = ProductAdminForm(data=data, instance=product)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertEqual(str(saved.price), '175')
        self.assertEqual(saved.image_url, 'https://new-shop.example/static/recovered-catalog/1.jpg')
        data['price'] = '-1'
        form = ProductAdminForm(data=data, instance=saved)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
