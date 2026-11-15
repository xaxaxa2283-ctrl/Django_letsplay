# Generated manually for the MoySklad read-only integration.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_cart_store_order_store_order_store_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='moysklad_assortment_id',
            field=models.UUIDField(
                blank=True,
                help_text='Идентификатор товара или модификации из МоегоСклада. Нужен для синхронизации цены и остатка.',
                null=True,
                unique=True,
                verbose_name='ID товара или модификации в МоемСкладе',
            ),
        ),
    ]
