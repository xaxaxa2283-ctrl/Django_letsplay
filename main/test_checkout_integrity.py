from django.test import TestCase
from django.urls import reverse
from main.models import Cart, CartItem, Category, Product, Order, Store


class CheckoutIntegrityTests(TestCase):
    def setUp(self):
        self.store, _ = Store.objects.get_or_create(slug='ekaterinburg', defaults={'name':'LetsPlay', 'city':'Екатеринбург'})
        self.cart = Cart.objects.create(session_key=self.client.session.session_key, store=self.store)
        category = Category.objects.create(name='Console', category_type='consoles')
        self.product = Product.objects.create(category=category, name='Console', slug='console', price='100.25')
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.data = {'name':'Buyer', 'phone':'123456789', 'email':'', 'delivery_method':'pickup',
                     'payment_method':'cash', 'personal_data_consent':'yes', 'comment':'Gift'}

    def test_invalid_contact_keeps_entered_values_and_does_not_create_order(self):
        self.data.update(email='not-an-email', delivery_method='courier', address='')
        response = self.client.post(reverse('main:checkout'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Buyer"')
        self.assertContains(response, 'value="not-an-email"')
        self.assertContains(response, 'Gift')
        self.assertContains(response, 'Укажите адрес доставки.')
        self.assertFalse(Order.objects.exists())
        self.assertTrue(self.cart.items.exists())

    def test_saved_total_equals_saved_rows_and_repeat_post_creates_no_duplicate(self):
        self.client.post(reverse('main:checkout'), self.data)
        order = Order.objects.get()
        self.assertEqual(order.total_price, sum(item.product_price * item.quantity for item in order.items.all()))
        self.product.price = '999'
        self.product.save()
        order.refresh_from_db()
        self.assertEqual(str(order.total_price), '300.75')
        self.client.post(reverse('main:checkout'), self.data)
        self.assertEqual(Order.objects.count(), 1)

    def test_forged_online_payment_and_overlong_name_are_rejected(self):
        self.data.update(name='X' * 201, payment_method='online')
        response = self.client.post(reverse('main:checkout'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())
