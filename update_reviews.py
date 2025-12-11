import os
import django
import random

# ⬇️ ВАЖНО: скопируй отсюда имя проекта из manage.py!
# Открой manage.py и найди строку:
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'XXXXX.settings')
# Вместо XXXXX подставь то, что у тебя там.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_site2.settings')

django.setup()

from main.models import Review


def main():
    count = 0

    for r in Review.objects.all():
        # Аватарка = первая буква имени, если её ещё нет
        if (not r.avatar) and r.name:
            r.avatar = r.name.strip()[0].upper()

        # Если лайков 0 — ставим случайное число
        if r.likes == 0:
            r.likes = random.randint(3, 40)  # можешь поменять диапазон

        r.save()
        count += 1

    print("Обновлено отзывов:", count)


if __name__ == "__main__":
    main()
