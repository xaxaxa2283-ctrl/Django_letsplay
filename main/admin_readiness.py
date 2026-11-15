"""Non-blocking completeness hints; field presence is not verification of facts."""


def product_readiness(product):
    missing = []
    category_type = product.category.category_type if product.category_id else None
    if category_type in ('consoles', 'disks') and not product.condition:
        missing.append('состояние')
    specs = product.specifications
    if not isinstance(specs, list) or not any(
        isinstance(row, dict) and str(row.get('label') or '').strip() and str(row.get('value') or '').strip()
        for row in specs
    ):
        missing.append('характеристики / комплектация')
    if not product.get_image_url():
        missing.append('изображение')
    elif product.get_image_url().split('?')[0].endswith('/no-photo.svg'):
        missing.append('фото товара вместо заглушки')
    prefix = 'Опубликован: ' if product.is_active else 'Черновик: '
    if missing:
        return prefix + 'нужно уточнить — ' + ', '.join(missing) + '. Сохранение разрешено; неизвестные данные не заполняйте предположениями.'
    return prefix + 'основные поля заполнены. Сверьте факты, комплект и актуальное наличие перед продажей.'


def store_readiness(store):
    missing = [label for field, label in (('city', 'город'), ('address', 'адрес'), ('phone', 'телефон'), ('opening_hours', 'время работы'))
               if not (getattr(store, field, '') or '').strip()]
    if missing:
        return 'Уточните: ' + ', '.join(missing) + '. Неизвестные данные можно оставить пустыми.'
    return 'Контактные поля заполнены. Проверьте, что они актуальны; заполненность не означает подтверждение.'


def offer_readiness(offer):
    notes = ['Подготовка: предложение пока не подключено к витрине и корзине.']
    if offer.availability == 'unknown':
        notes.append('Наличие не подтверждено.')
    elif offer.availability == 'available':
        notes.append('Проверьте фактический остаток: значение «В наличии» и дата редактирования не доказывают сверку склада.')
    else:
        notes.append('Указано отсутствие товара.')
    if offer.product_id and not offer.product.is_active:
        notes.append('Товар скрыт из каталога.')
    if offer.store_id:
        notes.append(store_readiness(offer.store))
    return ' '.join(notes)
