"""Read-only helper for mapping website cards to MoySklad assortment IDs."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from django.core.management.base import BaseCommand, CommandError

from main.models import Product
from main.moysklad import MoySkladAssortment, MoySkladClient, MoySkladError


REPLACEMENTS = (
    ('playstation', 'ps'),
    ('плейстейшен', 'ps'),
    ('приставка', ''),
    ('консоль', ''),
    ('дисководом', 'disc'),
    ('дисковода', 'disc'),
    ('дисковый', 'disc'),
    ('blu-ray', 'disc'),
    ('blu ray', 'disc'),
    ('digital', 'de'),
    ('бездисковая', 'nodisc'),
    ('без дисковода', 'nodisc'),
    ('б/у', 'used'),
    ('бу ', 'used '),
    ('новая', 'new'),
    ('новый', 'new'),
)


def normalized_tokens(value: str) -> set[str]:
    normalized = value.casefold()
    for source, replacement in REPLACEMENTS:
        normalized = normalized.replace(source, replacement)
    normalized = re.sub(r'\bps\s*(\d)\b', r'ps \1', normalized)
    return set(re.findall(r'[a-zа-я0-9]+', normalized))


def score(product_name: str, assortment_name: str) -> int:
    """A conservative ranking score; it never creates a mapping itself."""
    left = normalized_tokens(product_name)
    right = normalized_tokens(assortment_name)
    if 'заглушка' in right:
        return 0
    if not left or not right:
        return 0
    overlap = len(left & right) / len(left | right)
    text_similarity = SequenceMatcher(None, ' '.join(sorted(left)), ' '.join(sorted(right))).ratio()
    return round((overlap * 0.7 + text_similarity * 0.3) * 100)


class Command(BaseCommand):
    help = 'Показывает возможные соответствия карточек сайта ассортименту МойСклад. Ничего не изменяет.'

    def add_arguments(self, parser):
        parser.add_argument('--top', type=int, default=3, help='Число вариантов на карточку, от 1 до 10.')

    def handle(self, *args, **options):
        top = options['top']
        if not 1 <= top <= 10:
            raise CommandError('--top должен быть от 1 до 10.')
        try:
            assortment = MoySkladClient().list_assortment()
        except MoySkladError as exc:
            raise CommandError(str(exc)) from exc

        products = Product.objects.filter(is_active=True).order_by('name')
        self.stdout.write('Предпросмотр сопоставления. Результат не создаёт и не меняет связи.')
        for product in products:
            ranked = sorted(
                ((score(product.name, item.name), item) for item in assortment),
                key=lambda pair: pair[0],
                reverse=True,
            )[:top]
            self.stdout.write(f'\n[{product.id}] {product.name}')
            if product.moysklad_assortment_id:
                self.stdout.write(f'  Уже связан: {product.moysklad_assortment_id}')
            for value, item in ranked:
                self.stdout.write(f'  {value:>3}%  {item.id}  {item.name} ({item.code or "без артикула"})')
