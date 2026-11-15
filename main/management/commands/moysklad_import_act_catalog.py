"""Import active (ACT) MoySklad positions as linked LetsPlay catalogue cards."""

from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from main.models import Category, Product
from main.moysklad import MoySkladAssortment, MoySkladClient, MoySkladError


def classify(name: str) -> tuple[str, str | None, str, str]:
    """Return category type, platform, condition and firmware for an ACT row."""
    value = name.casefold()
    used = 'used' in value
    condition = 'used' if used else ('new' if 'new' in value else '')
    if 'ps 4' in value or 'ps4' in value or 'playstation 4' in value:
        platform = 'ps4'
    elif 'ps 5' in value or 'ps5' in value or 'playstation 5' in value:
        platform = 'ps5'
    elif 'xbox' in value:
        platform = 'xbox'
    elif 'switch' in value:
        platform = 'universal'
    else:
        platform = None
    if platform:
        category_type = 'consoles'
    elif ('игра' in value or re.search(r'\bgame\b', value)) and 'дисковод' not in value:
        category_type = 'disks'
    else:
        category_type = 'accessories'
    firmware = 'modified' if ('прошит' in value or 'hacked' in value) else ''
    return category_type, platform, condition, firmware


def display_name(source: str) -> str:
    value = re.sub(r'\bACT\b', '', source, flags=re.IGNORECASE)
    value = value.replace('_', ' ').replace('-', ' ')
    replacements = (
        (r'\bPS\s?5\b', 'PlayStation 5'),
        (r'\bPS\s?4\b', 'PlayStation 4'),
        (r'\bDE\b', 'Digital'),
        (r'\bBLU\s?RAY\b', 'Blu-ray'),
        (r'\bUSED\b', 'б/у'),
        (r'\bNEW\b', 'новая'),
        (r'\bПРОШИТАЯ\b', 'с прошивкой'),
        (r'\b1TB\b', '1 ТБ'),
        (r'\b512GB\b', '512 ГБ'),
        (r'\b825GB\b', '825 ГБ'),
    )
    for pattern, replacement in replacements:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
    value = re.sub(r'\s+', ' ', value).strip()
    return value[:200]


class Command(BaseCommand):
    help = 'Создаёт связанные с МойСкладом карточки для всех позиций, в названии которых есть ACT.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Создать карточки. Без флага выводится только план.')

    def handle(self, *args, **options):
        try:
            assortment = MoySkladClient().list_assortment()
        except MoySkladError as exc:
            raise CommandError(str(exc)) from exc
        candidates = [item for item in assortment if re.search(r'\bact\b', item.name, flags=re.IGNORECASE)]
        linked_ids = set(
            str(value) for value in Product.objects.exclude(moysklad_assortment_id__isnull=True)
            .values_list('moysklad_assortment_id', flat=True)
        )
        to_create = [item for item in candidates if item.id not in linked_ids]
        self.stdout.write(f'ACT-позиций в МойСклад: {len(candidates)}. Уже связаны: {len(candidates) - len(to_create)}. К созданию: {len(to_create)}.')
        for item in to_create:
            self.stdout.write(f'• {item.code or "—"}: {display_name(item.name)}')
        if not options['apply']:
            self.stdout.write('Это предпросмотр. Для создания используйте --apply.')
            return

        categories: dict[str, Category] = {}
        created = 0
        with transaction.atomic():
            for item in to_create:
                category_type, platform, condition, firmware = classify(item.name)
                category = categories.get(category_type)
                if category is None:
                    category = Category.objects.filter(category_type=category_type).order_by('id').first()
                    if category is None:
                        category = Category.objects.create(
                            name=dict(Category.CATEGORY_CHOICES)[category_type],
                            category_type=category_type,
                        )
                    categories[category_type] = category
                price = item.price_for(settings.MOYSKLAD_SITE_PRICE_TYPE)
                price = price if price is not None and price > 0 else Decimal('0')
                old_price = (
                    (price * Decimal('1.10')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                    if price > 0 else None
                )
                name = display_name(item.name)
                representative = Product.objects.filter(
                    category=category,
                    platform=platform,
                ).exclude(image='').exclude(image__isnull=True).order_by('id').first()
                product = Product.objects.create(
                    name=name,
                    slug=f'{slugify(name) or "catalog"}-{(item.code or item.id[:8]).casefold()}',
                    category=category,
                    price=price,
                    old_price=old_price,
                    image=representative.image if representative else None,
                    image_url=representative.image_url if representative else '',
                    badge='Цена уточняется' if price == 0 else '',
                    description='Наличие и цена обновляются из МоегоСклада. Комплектацию уточним перед покупкой.',
                    condition=condition,
                    firmware_status=firmware,
                    platform=platform,
                    in_stock=False,
                    is_active=True,
                    moysklad_assortment_id=item.id,
                )
                created += 1
                self.stdout.write(f'Создана карточка: {product.name}.')
        self.stdout.write(self.style.SUCCESS(f'Создано карточек: {created}.'))
