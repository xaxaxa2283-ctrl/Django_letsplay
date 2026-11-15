from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from main.models import Cart, CartItem, Category, Order, Product


class OrderAccessTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username='owner')
        self.other = get_user_model().objects.create_user(username='other')
        self.owned = self.make_order(user=self.owner)
        self.guest = self.make_order()

    def make_order(self, **extra):
        return Order.objects.create(customer_name='Private Customer',
            customer_email='private@example.com', customer_phone='+79991234567',
            delivery_method='pickup', payment_method='cash', total_price='100', **extra)

    def check_access(self, client, order, expected):
        for name in ('main:order_success', 'main:order_detail'):
            with self.subTest(route=name, order=order.pk, status=expected):
                response = client.get(reverse(name, kwargs={'order_id': order.pk}))
                self.assertEqual(response.status_code, expected)
                if expected == 404:
                    self.assertNotContains(response, 'private@example.com', status_code=404)
                    self.assertNotContains(response, '+79991234567', status_code=404)
                else:
                    self.assertIn('no-store', response['Cache-Control'])

    def test_anonymous_cannot_read_orders_by_guessing_ids(self):
        self.check_access(self.client, self.owned, 404)
        self.check_access(self.client, self.guest, 404)

    def test_account_owner_only_can_read_account_order(self):
        self.client.force_login(self.owner)
        self.check_access(self.client, self.owned, 200)
        self.check_access(self.client, self.guest, 404)
        self.client.force_login(self.other)
        self.check_access(self.client, self.owned, 404)
        self.check_access(self.client, self.guest, 404)

    def test_guest_session_does_not_grant_access_to_account_order(self):
        session = self.client.session
        session['guest_order_ids'] = [self.guest.pk, self.owned.pk]
        session.save()
        self.check_access(self.client, self.guest, 200)
        self.check_access(self.client, self.owned, 404)
        self.check_access(Client(), self.guest, 404)

    def test_checkout_grants_access_only_to_creating_guest_session(self):
        category = Category.objects.create(name='Consoles', category_type='consoles')
        product = Product.objects.create(name='Console', slug='console', price='100', category=category)
        session = self.client.session
        cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(cart=cart, product=product)
        response = self.client.post(reverse('main:checkout'), {
            'name': 'Private Customer', 'phone': '+79991234567',
            'email': 'private@example.com', 'personal_data_consent': 'yes',
            'delivery_method': 'pickup', 'payment_method': 'cash',
        })
        created = Order.objects.latest('pk')
        self.assertNotIn(created.pk, (self.guest.pk, self.owned.pk))
        self.assertRedirects(response, reverse('main:order_success', kwargs={'order_id': created.pk}))
        self.assertIn(created.pk, self.client.session['guest_order_ids'])
        self.check_access(self.client, created, 200)
        self.check_access(Client(), created, 404)
        self.assertFalse(cart.items.exists())
