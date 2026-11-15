from django.test import TestCase
from django.urls import reverse
from .models import Cart, CartItem, Category, Product, Order, Store


class OrderStoreTests(TestCase):
    def setUp(self):
        self.ekb = Store.objects.get(slug='ekaterinburg')
        self.yar = Store.objects.get(slug='yaroslavl')
        self.product = Product.objects.create(name='Console', price=100, category=Category.objects.create(name='Consoles', category_type='consoles'))
        self.cart = Cart.objects.create(session_key=self.client.session.session_key)
        CartItem.objects.create(cart=self.cart, product=self.product)
        self.data = {'name': 'Buyer', 'phone': '123456789', 'delivery_method': 'pickup', 'payment_method': 'cash', 'personal_data_consent': 'yes'}

    def test_checkout_assigns_store_and_preserves_name(self):
        response = self.client.get(reverse('main:checkout'))
        self.assertContains(response, self.ekb.name)
        self.data['store'] = self.yar.pk
        self.client.post(reverse('main:checkout'), self.data)
        order = Order.objects.get()
        self.assertEqual(order.store_id, self.ekb.pk)
        self.assertEqual(order.store_name, self.ekb.name)
        self.ekb.name = 'Renamed'
        self.ekb.save()
        order.refresh_from_db()
        self.assertEqual(order.store_name, 'LetsPlay Екатеринбург')

    def test_other_store_cannot_use_legacy_prices(self):
        self.cart.store = self.yar
        self.cart.save()
        response = self.client.post(reverse('main:checkout'), self.data)
        self.assertRedirects(response, reverse('main:cart_view'))
        self.assertFalse(Order.objects.exists())
        self.assertEqual(self.cart.items.count(), 1)
