import random
from datetime import datetime, timedelta
from django.utils import timezone
from main.models import Review

# --------------------
# Настройки
# --------------------
REAL_COUNT = 40
FAKE_COUNT = 1000

# Реальные: последние 60 дней, но НЕ сегодня (чтобы не светилось)
REAL_DAYS_RANGE = 60
REAL_EXCLUDE_LAST_DAYS = 1  # 1 = исключаем сегодня

# Фейки: с 2022 по "сейчас минус окно реальных"
FAKE_START_DATE = datetime(2022, 1, 1)
FAKE_MIN_AGE_DAYS = REAL_DAYS_RANGE + 10  # чтобы фейки были старее, чем реальные


FIRST_NAMES = [
    "Иван", "Алексей", "Сергей", "Дмитрий", "Никита", "Михаил", "Артём", "Андрей",
    "Екатерина", "Юлия", "Анна", "Мария", "Ольга", "Наталья", "Алина", "Виктория",
    "Павел", "Илья", "Кирилл", "Егор", "Владислав", "Роман", "Константин", "Глеб",
]

TEMPLATES = [
    "Всё супер: {what}. {extra}",
    "Покупал(а) {what} — {result}. {extra}",
    "Очень доволен(на) покупкой: {what}. {extra}",
    "Хороший магазин: {result}. {extra}",
    "Рекомендую! {extra} {result}.",
    "Быстро оформили и {result}. {extra}",
]

WHAT = [
    "PS5", "PS4", "DualSense", "геймпад", "подписку PS Plus", "наушники", "аксессуары",
    "игру", "карты пополнения", "подписку на 12 месяцев", "подписку Extra", "подписку Deluxe",
]

RESULT = [
    "доставили быстро", "всё работает отлично", "цена приятная", "упаковка идеальная",
    "подключили и помогли настроить", "ответили на все вопросы", "дали гарантию",
    "быстро связались после заказа", "всё соответствует описанию",
]

EXTRA = [
    "Персонал вежливый.",
    "Буду брать ещё.",
    "Спасибо!",
    "Покупкой доволен(на).",
    "Сервис на уровне.",
    "Всё честно и без сюрпризов.",
    "Приятно удивили скоростью.",
    "Рекомендую друзьям.",
    "Отдельное спасибо за консультацию.",
]


def random_dt_between(start, end):
    # start/end: aware datetime
    if start > end:
        start, end = end, start
    delta = end - start
    seconds = int(delta.total_seconds())
    return start + timedelta(seconds=random.randint(0, max(seconds, 1)))


def make_text():
    return random.choice(TEMPLATES).format(
        what=random.choice(WHAT),
        result=random.choice(RESULT),
        extra=random.choice(EXTRA),
    )


def rating_weighted_4_5():
    """Только 4–5, чтобы не было ниже 4"""
    # 80% пятёрок, 20% четвёрок
    return 5 if random.random() < 0.8 else 4


def likes_from_rating(r):
    """Лайки зависят от рейтинга (под 4–5)"""
    if r == 5:
        return random.randint(3, 60)
    return random.randint(1, 30)  # для 4


def main():
    now = timezone.now()

    # --------------------
    # 1) Берём первые 40 реальных и закрепляем
    # --------------------
    real_qs = Review.objects.order_by("id")[:REAL_COUNT]
    real_ids = list(real_qs.values_list("id", flat=True))

    if not real_ids:
        print("Нет ни одного отзыва в базе — сначала загрузи реальные отзывы.")
        return

    print(f"Найдено реальных для закрепления/обновления дат: {len(real_ids)}")

    # закрепляем + одобряем
    Review.objects.filter(id__in=real_ids).update(is_pinned=True, is_approved=True)

    # диапазон дат для реальных: последние 60 дней, но не сегодня
    real_start = now - timedelta(days=REAL_DAYS_RANGE)
    real_end = now - timedelta(days=REAL_EXCLUDE_LAST_DAYS)

    for r in Review.objects.filter(id__in=real_ids):
        r.date = random_dt_between(real_start, real_end)

        # аватар — первая буква имени
        if r.name:
            r.avatar = r.name.strip()[:1].upper()

        # рейтинг минимум 4 (если вдруг в реальных было иначе)
        if r.rating < 4:
            r.rating = 4

        r.save(update_fields=["date", "avatar", "rating"])

    print("✅ Реальным 40 обновили даты (не сегодня), аватары и закрепили.")

    # --------------------
    # 2) Создаём 1000 фейков
    # --------------------
    fake_end = now - timedelta(days=FAKE_MIN_AGE_DAYS)

    # start: 01.01.2022 (aware)
    fake_start = timezone.make_aware(FAKE_START_DATE) if timezone.is_naive(FAKE_START_DATE) else FAKE_START_DATE

    # подстраховка на всякий случай
    if fake_start > fake_end:
        fake_start = fake_end - timedelta(days=365)

    to_create = []
    for _ in range(FAKE_COUNT):
        name = random.choice(FIRST_NAMES)
        rating = rating_weighted_4_5()
        dt = random_dt_between(fake_start, fake_end)
        text = make_text()
        likes = likes_from_rating(rating)

        to_create.append(Review(
            name=name,
            text=text,
            rating=rating,
            likes=likes,
            avatar=name.strip()[:1].upper() if name else None,
            is_approved=True,
            is_pinned=False,
            date=dt,
        ))

    Review.objects.bulk_create(to_create, batch_size=200)
    print(f"✅ Создано фейковых отзывов: {FAKE_COUNT}")


main()
