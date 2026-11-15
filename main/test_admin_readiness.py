from django.test import TestCase
from main.admin import ProductAdminForm
from main.admin_readiness import product_readiness, store_readiness, offer_readiness
from main.models import Category, Product, Store, StoreOffer


class CatalogReadinessTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Consoles', category_type='consoles')

    def test_incomplete_active_product_warns_without_blocking_save(self):
        data = {'name':'Console', 'slug':'console', 'category':self.category.pk, 'price':'100',
                'rating':'5', 'variant_order':'0', 'is_active':'on', 'in_stock':'on'}
        form = ProductAdminForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        product = form.save()
        notice = product_readiness(product)
        for term in ('Опубликован', 'состояние', 'характеристики', 'изображение', 'Сохранение разрешено'):
            self.assertIn(term, notice)
        product.refresh_from_db()
        self.assertEqual(product.condition, '')
        self.assertTrue(product.is_active)

    def test_filled_fields_do_not_claim_verified_readiness(self):
        product = Product(category=self.category, condition='used', name='Console', price=100,
            image_url='/static/photo.jpg', specifications=[{'label':'Память', 'value':'1 ТБ'}])
        notice = product_readiness(product)
        self.assertIn('основные поля заполнены', notice)
        self.assertIn('Сверьте', notice)
        product.image_url = '/static/recovered-catalog/no-photo.svg'
        self.assertIn('заглушки', product_readiness(product))

    def test_missing_store_data_and_unknown_offer_are_explicit(self):
        store = Store.objects.create(name='Shop', slug='shop', city='Екатеринбург')
        self.assertIn('адрес', store_readiness(store))
        product = Product.objects.create(category=self.category, name='Console', slug='console', price=100, is_active=False)
        offer = StoreOffer(store=store, product=product, price=100)
        notice = offer_readiness(offer)
        for term in ('не подключено', 'Наличие не подтверждено', 'скрыт', 'адрес'):
            self.assertIn(term, notice)
        offer.availability = 'available'
        self.assertIn('не доказывают', offer_readiness(offer))
