from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)



from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from main.models import Review
from main.services.reviews_stats import invalidate_reviews_stats_cache

@receiver([post_save, post_delete], sender=Review)
def review_changed(sender, instance, **kwargs):
    invalidate_reviews_stats_cache()