from django.urls import path

from . import views

app_name = "legal"

urlpatterns = [
    path("privacy/", views.privacy, name="privacy"),
    path("consent/", views.consent, name="consent"),
    path("offer/", views.offer, name="offer"),
    path("returns/", views.returns, name="returns"),
    path("requisites/", views.requisites, name="requisites"),
    path("cookies/", views.cookies, name="cookies"),
]
