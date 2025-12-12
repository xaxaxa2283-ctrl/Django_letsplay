from django.core.cache import cache
from django.db.models import Avg
from main.models import Review

STATS_CACHE_KEY = "reviews:stats:v1"
STATS_TTL = 60 * 5  # 5 минут

def get_reviews_stats():
    stats = cache.get(STATS_CACHE_KEY)
    if stats is not None:
        return stats

    qs = Review.objects.filter(is_approved=True)

    stats = {
        "total_clients": qs.count(),
        "rating": round(qs.aggregate(avg=Avg("rating"))["avg"] or 0, 1),
        "recommendations": 99,
    }
    cache.set(STATS_CACHE_KEY, stats, STATS_TTL)
    return stats

def invalidate_reviews_stats_cache():
    cache.delete(STATS_CACHE_KEY)
