from django.core.management.base import BaseCommand, CommandError

from main.moysklad import MoySkladClient, MoySkladError


class Command(BaseCommand):
    help = 'Проверяет доступ к МойСклад и выводит доступные склады. Ничего не изменяет.'

    def handle(self, *args, **options):
        try:
            warehouses = MoySkladClient().list_warehouses()
        except MoySkladError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f'Подключение к МойСклад выполнено. Складов: {len(warehouses)}.'))
        for warehouse in warehouses:
            self.stdout.write(f'{warehouse.name}\t{warehouse.id}')
