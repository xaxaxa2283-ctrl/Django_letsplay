import json
from pathlib import Path
from datetime import datetime

from main.models import Review

# 1. Читаем JSON (лежит в той же папке)
path = Path("reviews_fixture.json")
data = json.loads(path.read_text(encoding="utf-8"))

print(f"Всего объектов в файле: {len(data)}")

Review.objects.all().delete()
created = 0

for obj in data:
    if obj.get("model") not in ("main.review", "reviews.reviews", "review.reviews"):
        continue

    fields = obj["fields"]

    name = fields.get("name", "")
    text = fields.get("text", "")
    count_stars = fields.get("count_stars", "")

    # рейтинг
    rating = count_stars.count("★")

    # дата
    dt = None
    if fields.get("date"):
        try:
            dt = datetime.fromisoformat(fields["date"])
        except:
            pass

    r = Review(
        name=name,
        text=text,
        rating=rating,
        is_approved=True,
    )
    if dt:
        r.date = dt

    r.save()
    created += 1

print("Создано:", created)
