from django.db import migrations


def seed(apps, schema_editor):
    Store = apps.get_model('main', 'Store')
    Offer = apps.get_model('main', 'StoreOffer')
    Product = apps.get_model('main', 'Product')
    alias = schema_editor.connection.alias
    ekb, _ = Store.objects.using(alias).get_or_create(slug='ekaterinburg', defaults={'name': 'LetsPlay Екатеринбург', 'city': 'Екатеринбург'})
    Store.objects.using(alias).get_or_create(slug='yaroslavl', defaults={'name': 'LetsPlay Ярославль', 'city': 'Ярославль'})
    for product in Product.objects.using(alias).all().iterator():
        Offer.objects.using(alias).get_or_create(store=ekb, product=product, defaults={'price': product.price, 'availability': 'available' if product.in_stock else 'unavailable'})


class Migration(migrations.Migration):
    dependencies = [('main', '0010_store_storeoffer_and_more')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
