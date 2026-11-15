from django.core.management.base import BaseCommand, CommandError

from main.models import Product
from main.moysklad import MoySkladClient, MoySkladError


class Command(BaseCommand):
    help = 'Связывает одну карточку сайта с одной подтверждённой позицией МойСклад.'

    def add_arguments(self, parser):
        parser.add_argument('product_id', type=int, help='ID карточки сайта.')
        parser.add_argument('assortment_id', help='ID товара или модификации из МоегоСклада.')

    def handle(self, *args, **options):
        try:
            product = Product.objects.get(pk=options['product_id'])
        except Product.DoesNotExist as exc:
            raise CommandError('Карточка сайта не найдена.') from exc
        try:
            items = MoySkladClient().list_assortment()
        except MoySkladError as exc:
            raise CommandError(str(exc)) from exc
        match = next((item for item in items if item.id == options['assortment_id']), None)
        if match is None:
            raise CommandError('Позиция с таким ID не найдена в МойСклад.')
        if product.moysklad_assortment_id and str(product.moysklad_assortment_id) != match.id:
            raise CommandError('Карточка уже связана с другой позицией. Измените связь в админке после проверки.')
        product.moysklad_assortment_id = match.id
        product.save(update_fields=['moysklad_assortment_id', 'updated_at'])
        self.stdout.write(self.style.SUCCESS(f'«{product.name}» связан с «{match.name}».'))
