from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP

from main.models import Product, Store, StoreOffer
from main.moysklad import MoySkladClient, MoySkladError


class Command(BaseCommand):
    help = (
        'Сверяет наличие уже сопоставленных карточек с МойСкладом. '
        'По умолчанию только показывает изменения; для записи укажите --apply.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--store', default='ekaterinburg', help='Код магазина сайта.')
        parser.add_argument('--apply', action='store_true', help='Записать изменения после предпросмотра.')

    def handle(self, *args, **options):
        try:
            store = Store.objects.get(slug=options['store'])
        except Store.DoesNotExist as exc:
            raise CommandError(f'Магазин с кодом «{options["store"]}» не найден.') from exc
        if not store.moysklad_warehouse_id:
            raise CommandError('Для магазина не задан склад МойСклад. Сначала выполните moysklad_bind_store.')

        products = list(
            Product.objects.exclude(moysklad_assortment_id__isnull=True).order_by('name')
        )
        if not products:
            self.stdout.write(self.style.WARNING(
                'Нет сопоставленных карточек. Заполните «ID товара или модификации в МоемСкладе» '
                'у нужных товаров в админке; новые карточки эта команда не создаёт.'
            ))
            return

        client = MoySkladClient()
        try:
            stock = client.list_stock_for_store(str(store.moysklad_warehouse_id))
            assortment = {item.id: item for item in client.list_assortment()}
        except MoySkladError as exc:
            raise CommandError(str(exc)) from exc

        changes = []
        missing = []
        missing_prices = []
        price_type = settings.MOYSKLAD_SITE_PRICE_TYPE
        for product in products:
            current = stock.get(str(product.moysklad_assortment_id))
            if current is None:
                missing.append(product)
                # A missing row means that the selected warehouse has no
                # balance for this linked item. Do not leave a sold item on
                # the storefront as available.
                available = False
            else:
                available = current.free_stock >= 1
            source = assortment.get(str(product.moysklad_assortment_id))
            site_price = source.price_for(price_type) if source else None
            if site_price is None or site_price <= 0:
                missing_prices.append(product)
                site_price = None
            old_price = (
                (site_price * Decimal('1.10')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                if site_price is not None else None
            )
            price_changed = site_price is not None and (
                product.price != site_price or product.old_price != old_price
            )
            if product.in_stock != available or price_changed:
                changes.append((product, available, current, site_price, old_price))

        mode = 'ПРИМЕНЕНИЕ' if options['apply'] else 'ПРЕДПРОСМОТР'
        self.stdout.write(f'{mode}: магазин «{store.name}», сопоставленных карточек: {len(products)}.')
        for product, available, current, site_price, old_price in changes:
            state = 'в наличии' if available else 'нет в наличии'
            if current is None:
                line = f'• {product.name}: {state} (в отчёте склада позиции нет)'
                if site_price is not None:
                    line += f'; цена {site_price:f} ₽, старая {old_price:f} ₽'
                self.stdout.write(line + '.')
                continue
            line = (
                f'• {product.name}: {state} '
                f'(остаток {current.stock:f}, резерв {current.reserve:f})'
            )
            if site_price is not None:
                line += f'; цена {site_price:f} ₽, старая {old_price:f} ₽'
            self.stdout.write(line + '.')
        if missing:
            self.stdout.write(self.style.WARNING(
                f'В отчёте не найдены {len(missing)} карточек; они будут отмечены как распроданные: '
                + ', '.join(product.name for product in missing)
            ))
        if missing_prices:
            self.stdout.write(self.style.WARNING(
                f'Нет ненулевой цены типа «{price_type}» у {len(missing_prices)} карточек; '
                'их текущая цена сайта сохранена.'
            ))
        if not changes:
            self.stdout.write(self.style.SUCCESS('Изменений наличия нет.'))

        if not options['apply']:
            self.stdout.write('Для сохранения после проверки запустите команду с --apply.')
            return

        with transaction.atomic():
            for product, available, current, site_price, old_price in changes:
                product.in_stock = available
                fields = ['in_stock', 'updated_at']
                if site_price is not None:
                    product.price = site_price
                    product.old_price = old_price
                    fields.extend(['price', 'old_price'])
                product.save(update_fields=fields)
                StoreOffer.objects.update_or_create(
                    store=store,
                    product=product,
                    defaults={
                        'price': product.price,
                        'availability': 'available' if available else 'unavailable',
                    },
                )
        self.stdout.write(self.style.SUCCESS(f'Обновлено карточек: {len(changes)}.'))
