from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

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

        try:
            stock = MoySkladClient().list_stock_for_store(str(store.moysklad_warehouse_id))
        except MoySkladError as exc:
            raise CommandError(str(exc)) from exc

        changes = []
        missing = []
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
            if product.in_stock != available:
                changes.append((product, available, current))

        mode = 'ПРИМЕНЕНИЕ' if options['apply'] else 'ПРЕДПРОСМОТР'
        self.stdout.write(f'{mode}: магазин «{store.name}», сопоставленных карточек: {len(products)}.')
        for product, available, current in changes:
            state = 'в наличии' if available else 'нет в наличии'
            if current is None:
                self.stdout.write(f'• {product.name}: {state} (в отчёте склада позиции нет).')
                continue
            self.stdout.write(
                f'• {product.name}: {state} '
                f'(остаток {current.stock:f}, резерв {current.reserve:f}).'
            )
        if missing:
            self.stdout.write(self.style.WARNING(
                f'В отчёте не найдены {len(missing)} карточек; они будут отмечены как распроданные: '
                + ', '.join(product.name for product in missing)
            ))
        if not changes:
            self.stdout.write(self.style.SUCCESS('Изменений наличия нет.'))

        if not options['apply']:
            self.stdout.write('Для сохранения после проверки запустите команду с --apply.')
            return

        with transaction.atomic():
            for product, available, current in changes:
                product.in_stock = available
                product.save(update_fields=['in_stock', 'updated_at'])
                StoreOffer.objects.update_or_create(
                    store=store,
                    product=product,
                    defaults={
                        'price': product.price,
                        'availability': 'available' if available else 'unavailable',
                    },
                )
        self.stdout.write(self.style.SUCCESS(f'Обновлено карточек: {len(changes)}.'))
