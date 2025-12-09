# letsplay/urls.py
"""
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
path('catalog/catalog_detail/<int:product_id>/', views.catalog_detail, name='catalog_detail'),

]"""
from django.contrib.auth import views as auth_views
from main import views,views_auth
from django.urls import path


app_name = 'letsplay'

from django.contrib.auth import views as auth_views
from main import views
from django.urls import path

app_name = 'letsplay'

# letsplay/urls.py

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/load_more/', views.load_more_products, name='load_more_products'),

    # Детальная страница
    path('catalog/catalog_detail/<int:product_id>/', views.catalog_detail, name='catalog_detail'),
    path('catalog/<slug:slug>/', views.catalog_detail_by_slug, name='catalog_detail_by_slug'),

    path('reviews/', views.reviews, name='reviews'),
    path('reviews/load_more/', views.load_more_reviews, name='load_more_reviews'),

    # ✅ Добавь этот маршрут:
    path('cart/', views.cart_view, name='cart_view'),

    # Управление корзиной
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),

    # API
    path('api/data/', views.cart_data_api, name='cart_data_api'),

    # Оформление заказа
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/success/<int:order_id>/', views.order_success_view, name='order_success'),

    # Личный кабинет
    #path('my-orders/', views.my_orders_view, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),

    # Регистрация / вход
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('api/register/', views_auth.api_register, name='api_register'),
    path('api/login/', views_auth.api_login, name='api_login'),
    path('my-orders/', views.my_orders_view, name='my_orders_page'),
    path('api/logout/', views_auth.api_logout, name='api_logout'),
    path('auth/', views.auth_page_view, name='auth_page'),
    path('review/<int:review_id>/like/', views.like_review, name='like_review'),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart-count/", views.cart_count, name="cart_count"),
path("cart/item/<int:product_id>/", views.get_cart_item, name="get_cart_item"),
path("privacy/", views.privacy_policy, name="privacy_policy"),
    path("services/gifts/", views.service_gifts, name="service_gifts"),
    path("services/console-selection/", views.service_console_selection, name="service_console_selection"),
    path("services/setup/", views.service_setup, name="service_setup"),
    path("delivery/", views.delivery_page, name="delivery"),
    path("warranty/", views.warranty_page, name="warranty"),
    path("support/", views.support_page, name="support"),

]






# config/urls.py (главный urls.py проекта)

