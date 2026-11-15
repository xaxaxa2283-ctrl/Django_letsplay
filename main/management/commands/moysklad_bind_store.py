from django.core.management.base import BaseCommand, CommandError

from main.models import Store
from main.moysklad import MoySkladClient, MoySkladError


class Command(BaseCommand):
    help = 'Связывает магазин сайта со складом МойСклад по точному названию. Не изменяет МойСклад.'

    def add_arguments(self, parser):
        parser.add_argument('store_slug', help='Код магазина на сайте, например ekaterinburg')
        parser.add_argument('warehouse_name', help='Точное название склада в МоемСкладе')

    def handle(self, *args, **options):
        try:
            store = Store.objects.get(slug=options['store_slug'])
        except Store.DoesNotExist as exc:
            raise CommandError('Магазин сайта с таким кодом не найден.') from exc

        try:
            warehouses = MoySkladClient().list_warehouses()
        except MoySkladError as exc:
            raise CommandError(str(exc)) from exc

        desired = options['warehouse_name'].casefold().strip()
        matches = [item for item in warehouses if item.name.casefold().strip() == desired]
        if len(matches) != 1:
            raise CommandError('Не найден единственный склад с таким точным названием.')

        store.moysklad_warehouse_id = matches[0].id
        store.save(update_fields=['moysklad_warehouse_id'])
        self.stdout.write(self.style.SUCCESS(
            f'Магазин «{store.name}» связан со складом «{matches[0].name}» ({matches[0].id}).'
        ))
