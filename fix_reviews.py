import random
from datetime import datetime, timedelta
from django.utils import timezone
from main.models import Review

def random_dt_between(start, end):
    if start > end:
        start, end = end, start
    delta = end - start
    seconds = int(delta.total_seconds())
    return start + timedelta(seconds=random.randint(0, max(seconds, 1)))

now = timezone.now()

fake_start = timezone.make_aware(datetime(2022, 1, 1))
fake_end = now - timedelta(days=70)

real_start = now - timedelta(days=60)
real_end = now - timedelta(hours=3)

# 1) Находим закреплённые (твои реальные 40)
pinned = Review.objects.filter(is_pinned=True)

for r in pinned:
    # рейтинг минимум 4
    if r.rating < 4:
        r.rating = 4
    # дата в последних 60 дней
    r.date = random_dt_between(real_start, real_end)
    # аватар - первая буква
    r.avatar = (r.name.strip()[:1].upper() if r.name else None)
    r.save(update_fields=["rating", "date", "avatar"])

print(f"✅ Обновлено закреплённых: {pinned.count()}")

# 2) Остальные (фейки)
others = Review.objects.filter(is_pinned=False)

updated = 0
for r in others.iterator():
    # рейтинг только 4-5
    if r.rating < 4:
        r.rating = 4
    if r.rating > 5:
        r.rating = 5

    # дата в диапазоне 2022 .. (сегодня-70д)
    r.date = random_dt_between(fake_start, fake_end)

    # аватар - первая буква
    r.avatar = (r.name.strip()[:1].upper() if r.name else None)

    r.save(update_fields=["rating", "date", "avatar"])
    updated += 1

print(f"✅ Обновлено остальных: {updated}")
