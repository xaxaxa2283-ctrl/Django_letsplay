from django.core.management.base import BaseCommand, CommandError

from main.moysklad import MoySkladClient, MoySkladError


class Command(BaseCommand):
    help = 'Выводит ассортимент МойСклад для проверки сопоставления. Ничего не изменяет.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=100, help='Сколько строк вывести, максимум 500.')

    def handle(self, *args, **options):
        limit = options['limit']
        if not 1 <= limit <= 500:
            raise CommandError('Параметр --limit должен быть от 1 до 500.')
        try:
            assortment = MoySkladClient().list_assortment()
        except MoySkladError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f'Ассортимент МоегоСклада: {len(assortment)} позиций.'))
        self.stdout.write('ID\tТип\tНаименование\tАртикул\tЦены')
        for item in assortment[:limit]:
            prices = ', '.join(f'{label}: {amount:f} ₽' for label, amount in item.prices) or '—'
            self.stdout.write(f'{item.id}\t{item.entity_type or "—"}\t{item.name}\t{item.code or "—"}\t{prices}')
        if len(assortment) > limit:
            self.stdout.write(f'Показаны первые {limit} позиций. Для большего списка используйте --limit до 500.')
