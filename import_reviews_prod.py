# import_reviews_prod.py
import json
from pathlib import Path
from datetime import datetime

from main.models import Review


def run():
    path = Path("reviews_fixture.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    print(f"Всего объектов в файле: {len(data)}")

    created_count = 0
    skipped_count = 0

    for obj in data:
        # Берём только объекты с отзывами
        if obj.get("model") not in ("main.review", "review.reviews", "reviews.reviews"):
            continue

        fields = obj["fields"]

        name = fields.get("name", "").strip()
        text = fields.get("text", "").strip()
        date_str = fields.get("date")
        count_stars = fields.get("count_stars", "")

        if not name or not text:
            skipped_count += 1
            continue

        # Чтобы не плодить дубликаты, проверим по имени и тексту
        if Review.objects.filter(name=name, text=text).exists():
            skipped_count += 1
            continue

        # Преобразуем символы звёзд в рейтинг
        rating = 5
        if "★ ★ ★ ★ ★" in count_stars:
            rating = 5
        elif "★ ★ ★ ★" in count_stars:
            rating = 4
        elif "★ ★ ★" in count_stars:
            rating = 3
        elif "★ ★" in count_stars:
            rating = 2
        elif "★" in count_stars:
            rating = 1

        # Парсим дату (если есть)
        dt = None
        if date_str:
            for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    dt = datetime.strptime(date_str, fmt)
                    break
                except Exception:
                    continue

        review = Review(
            name=name,
            text=text,
            rating=rating,
            is_approved=True,
        )

        if dt is not None:
            review.date = dt

        review.save()
        created_count += 1

    print(f"Создано отзывов: {created_count}, пропущено (дубликаты/пустые): {skipped_count}")


run()
