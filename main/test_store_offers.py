from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError, transaction
from .models import Category, Product, Store, StoreOffer


class StoreOfferTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test console', price=100, category=Category.objects.create(name='Consoles', category_type='consoles'))
        self.ekb = Store.objects.get(slug='ekaterinburg')
        self.yar = Store.objects.get(slug='yaroslavl')

    def test_independent_prices_and_unknown_stock(self):
        first = StoreOffer.objects.create(store=self.ekb, product=self.product, price=110, availability='available')
        second = StoreOffer.objects.create(store=self.yar, product=self.product, price=120)
        self.assertEqual(second.availability, 'unknown')
        second.price = 130
        second.save()
        first.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(first.price, Decimal('110'))
        self.assertEqual(self.product.price, Decimal('100'))

    def test_duplicate_and_negative_price_rejected(self):
        StoreOffer.objects.create(store=self.ekb, product=self.product, price=100)
        with self.assertRaises(IntegrityError), transaction.atomic():
            StoreOffer.objects.create(store=self.ekb, product=self.product, price=200)
        with self.assertRaises(IntegrityError), transaction.atomic():
            StoreOffer.objects.create(store=self.yar, product=self.product, price=-1)

    def test_seed_preserves_existing_offers(self):
        from importlib import import_module
        from django.apps import apps
        from django.db import connection
        seed = import_module('main.migrations.0011_seed_stores').seed
        from types import SimpleNamespace
        editor = SimpleNamespace(connection=connection)
        seed(apps, editor)
        offer = StoreOffer.objects.get(store=self.ekb, product=self.product)
        self.assertEqual(offer.price, self.product.price)
        self.assertFalse(StoreOffer.objects.filter(store=self.yar).exists())
        offer.price = 150
        offer.save()
        seed(apps, editor)
        offer.refresh_from_db()
        self.assertEqual(offer.price, Decimal('150'))
