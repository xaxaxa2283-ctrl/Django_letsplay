# letsplay/urls.py

from django.urls import path
from . import views

app_name = 'letsplay'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/load_more/', views.load_more_products, name='load_more_products'),
    path('reviews/', views.reviews, name='reviews'),
path('reviews/load_more/', views.load_more_reviews, name='load_more_reviews'),
path('catalog/catalog_detail/', views.catalog_detail, name='catalog_detail'),
]


# config/urls.py (главный urls.py проекта)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('letsplay.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"""
