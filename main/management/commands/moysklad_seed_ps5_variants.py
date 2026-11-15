"""Create the confirmed PS5 Slim variants and bind them to MoySklad."""

from __future__ import annotations

from copy import copy

from django.core.management.base import BaseCommand
from django.db import transaction

from main.models import Product, ProductImage


MAPPINGS = (
    # Existing customer-facing cards become the new variants.
    (2, 'PlayStation 5 Slim Blu-ray', 'new', 'ps5-slim-bluray', 'С дисководом · новая', 0,
     '245e6a54-b82b-11f1-0a80-14bd001cdf14'),
    (3, 'PlayStation 5 Slim Digital', 'new', 'ps5-slim-digital', 'Без дисковода · новая', 0,
     '4dadb421-b82b-11f1-0a80-1bab001df92d'),
    (8, 'PlayStation 5 Fat Blu-ray', 'used', 'ps5-fat-bluray', 'С дисководом · б/у', 0,
     '48cbcf35-b82c-11f1-0a80-14bd001d0c44'),
    (9, 'PlayStation 5 Fat Digital', 'used', 'ps5-fat-digital', 'Без дисковода · б/у', 0,
     '5b21a80b-b82c-11f1-0a80-1bab001e2c28'),
    (16, 'PlayStation 5 Pro с дисководом 2 ТБ', 'new', 'ps5-pro-2tb', 'С дисководом · 2 ТБ', 0,
     '088f3e41-b82c-11f1-0a80-0499001d7c31'),
)

USED_SLIM_VARIANTS = (
    (2, 'PlayStation 5 Slim Blu-ray б/у', 'ps5-slim-bluray', 'С дисководом · б/у', 1,
     '38c57931-b82b-11f1-0a80-172d001e6dcf'),
    (3, 'PlayStation 5 Slim Digital б/у', 'ps5-slim-digital', 'Без дисковода · б/у', 1,
     '7736bad2-b82b-11f1-0a80-0bb5001d6be9'),
)


class Command(BaseCommand):
    help = 'Создаёт подтверждённые карточки PS5 Slim (новая и б/у) и связывает их с МойСкладом.'

    def _configure(self, product, *, name, condition, group, variant_name, order, assortment_id):
        product.name = name
        product.condition = condition
        product.variant_group = group
        product.variant_name = variant_name
        product.variant_order = order
        product.moysklad_assortment_id = assortment_id
        product.is_active = True
        product.save()
        return product

    def _copy_images(self, source, target):
        for image in source.images.all():
            ProductImage.objects.get_or_create(
                product=target,
                image=image.image.name,
                defaults={'order': image.order},
            )

    def handle(self, *args, **options):
        with transaction.atomic():
            for product_id, name, condition, group, variant_name, order, assortment_id in MAPPINGS:
                product = Product.objects.get(pk=product_id)
                self._configure(
                    product, name=name, condition=condition, group=group,
                    variant_name=variant_name, order=order, assortment_id=assortment_id,
                )
                self.stdout.write(f'Настроена карточка: {product.name}.')

            for source_id, name, group, variant_name, order, assortment_id in USED_SLIM_VARIANTS:
                source = Product.objects.get(pk=source_id)
                product = Product.objects.filter(moysklad_assortment_id=assortment_id).first()
                if product is None:
                    product = copy(source)
                    product.pk = None
                    product.id = None
                    product.name = name
                    product.slug = None
                    product.created_at = None
                    product.updated_at = None
                    product.moysklad_assortment_id = None
                    product.save()
                    self._copy_images(source, product)
                self._configure(
                    product, name=name, condition='used', group=group,
                    variant_name=variant_name, order=order, assortment_id=assortment_id,
                )
                self.stdout.write(f'Подготовлена карточка: {product.name}.')

            # The generic Pro card duplicates the explicit 2 TB disc version.
            legacy_pro = Product.objects.get(pk=1)
            legacy_pro.is_active = False
            legacy_pro.save(update_fields=['is_active', 'updated_at'])
        self.stdout.write(self.style.SUCCESS('PS5 Slim и PS5 Pro подготовлены к синхронизации остатков.'))
