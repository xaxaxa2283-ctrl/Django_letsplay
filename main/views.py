# letsplay/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Product, Review, Category

from django.utils import timezone


# cart_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.db.models import Sum, F, Q
import json


from .models import Cart, CartItem, Order, OrderItem, Store
from .services.reviews_stats import get_reviews_stats
from .seo import product_schema


def home(request):
    #Главная страница
    context = {
        'page': 'home',
        'title': 'LetsPlay — Магазин PlayStation в Екатеринбурге',
        'featured_products': Product.objects.filter(is_active=True, category__category_type='consoles').exclude(slug__isnull=True).exclude(slug='').select_related('category').order_by('-in_stock', 'id')[:4]
    }
    return render(request, 'main/home.html', context)

def about(request):
    #Страница О нас
    context = {
        'page': 'about',
        'title': 'О нас — LetsPlay Екатеринбург',
        'team': [
            {
                'name': 'Денис',
                'role': 'Основатель и директор',
                'description': 'Геймер с 15-летним стажем, создал LetsPlay чтобы делиться любовью к PlayStation'
            },
            {
                'name': 'Иван',
                'role': 'Менеджер по продажам',
                'description': 'Эксперт по консолям, поможет выбрать идеальную конфигурацию для ваших нужд'
            }
        ]
    }
    return render(request, 'main/about.html', context)




"""
from django.shortcuts import render
from django.http import JsonResponse

# Список товаров как и раньше
PRODUCTS = [
    {
        'id': 1,
        'name': 'PlayStation 5 Pro',
        'category': 'consoles',
        'price': 79990,
        'old_price': 89990,
        'image': '/static/images/ps5-pro.jpg',
        'badge': 'Хит продаж',
        'features': ['2TB SSD', '+ 700 игр', 'Ray Tracing'],
        'rating': 5,
    },
    {
        'id': 2,
        'name': 'PlayStation 5 Slim',
        'category': 'consoles',
        'price': 54990,
        'old_price': 64990,
        'image': '/static/images/ps5-slim.jpg',
        'badge': '+ 700 игр',
        'features': ['1TB SSD', 'Компактный дизайн', 'DualSense'],
        'rating': 5,
    },
    {
        'id': 3,
        'name': 'PlayStation 4 Pro',
        'category': 'consoles',
        'price': 32990,
        'image': '/static/images/ps4-pro.jpg',
        'badge': '+ 700 игр',
        'features': ['1TB HDD', '4K Gaming', 'HDR'],
        'rating': 5,
    },
    {
        'id': 4,
        'name': 'DualSense Controller',
        'category': 'accessories',
        'price': 6990,
        'image': '/static/images/dualsense.jpg',
        'features': ['Haptic Feedback', 'Adaptive Triggers', 'Built-in Mic'],
        'rating': 5,
    },
    {
        'id': 5,
        'name': 'PlayStation VR2',
        'category': 'accessories',
        'price': 59990,
        'old_price': 69990,
        'image': '/static/images/psvr2.jpg',
        'badge': 'Новинка',
        'features': ['4K HDR', 'Eye Tracking', '110° FOV'],
        'rating': 5,
    },
    {
        'id': 6,
        'name': 'PS Plus Premium 12 месяцев',
        'category': 'subscriptions',
        'price': 7499,
        'features': ['Онлайн игры', 'Каталог игр', 'Классика PS'],
        'rating': 5,
    },
    {
        'id': 7,
        'name': 'PS Plus Deluxe 12 месяцев',
        'category': 'subscriptions',
        'price': 9499,
        'features': ['Больше игр', 'Классика PS', 'Облачное хранение'],
        'rating': 5,
    },
    {
        'id': 8,
        'name': 'EA Play 12 месяцев',
        'category': 'subscriptions',
        'price': 3999,
        'features': ['Игры EA', 'Бонусы', 'Демо версии'],
        'rating': 4,
    },
    {        'id': 9,
        'name': 'PlayStation 5 Pro',
        'category': 'consoles',
        'price': 79990,
        'old_price': 89990,
        'image': '/static/images/ps5-pro.jpg',
        'badge': 'Хит продаж',
        'features': ['2TB SSD', '+ 700 игр', 'Ray Tracing'],
        'rating': 5,
    },
    {
        'id': 10,
        'name': 'PlayStation 5 Slim',
        'category': 'consoles',
        'price': 54990,
        'old_price': 64990,
        'image': '/static/images/ps5-slim.jpg',
        'badge': '+ 700 игр',
        'features': ['1TB SSD', 'Компактный дизайн', 'DualSense'],
        'rating': 5,
    },
    {
        'id': 11,
        'name': 'PlayStation 4 Pro',
        'category': 'consoles',
        'price': 32990,
        'image': '/static/images/ps4-pro.jpg',
        'badge': '+ 700 игр',
        'features': ['1TB HDD', '4K Gaming', 'HDR'],
        'rating': 5,
    },
    {
        'id': 12,
        'name': 'DualSense Controller',
        'category': 'accessories',
        'price': 6990,
        'image': '/static/images/dualsense.jpg',
        'features': ['Haptic Feedback', 'Adaptive Triggers', 'Built-in Mic'],
        'rating': 5,
    },
    {
        'id': 13,
        'name': 'PlayStation VR2',
        'category': 'accessories',
        'price': 59990,
        'old_price': 69990,
        'image': '/static/images/psvr2.jpg',
        'badge': 'Новинка',
        'features': ['4K HDR', 'Eye Tracking', '110° FOV'],
        'rating': 5,
    },
    {
        'id': 14,
        'name': 'PS Plus Premium 12 месяцев',
        'category': 'subscriptions',
        'price': 7499,
        'features': ['Онлайн игры', 'Каталог игр', 'Классика PS'],
        'rating': 5,
    },
    {
        'id': 15,
        'name': 'PS Plus Deluxe 12 месяцев',
        'category': 'subscriptions',
        'price': 9499,
        'features': ['Больше игр', 'Классика PS', 'Облачное хранение'],
        'rating': 5,
    },
    {
        'id': 16,
        'name': 'EA Play 12 месяцев',
        'category': 'subscriptions',
        'price': 3999,
        'features': ['Игры EA', 'Бонусы', 'Демо версии'],
        'rating': 4,
    },
]

#Страница отзывов
reviews_list = [
    {
        'id': 1,
        'name': 'Иван Петров',
        'date': '27 октября 2025',
        'rating': 5,
        'text': 'Отличный магазин! Купил PS5 Pro и очень доволен. Ребята все объяснили, помогли с выбором игр, настроили приставку прямо в магазине.',
        'avatar': 'И',
        'likes': 24,
    },
    {
        'id': 2,
        'name': 'Алена Смирнова',
        'date': '28 октября 2025',
        'rating': 5,
        'text': 'Брала PS4 в подарок сыну на день рождения. Консультанты очень дружелюбные, посоветовали хорошие игры для ребенка.',
        'avatar': 'А',
        'likes': 18,
    },
    {
        'id': 3,
        'name': 'Дарья Козлова',
        'date': '29 октября 2025',
        'rating': 5,
        'text': 'Лучший магазин PlayStation в городе! Покупала геймпад DualSense. Цены адекватные, все оригинальное.',
        'avatar': 'Д',
        'likes': 31,
    },
    {
        'id': 4,
        'name': 'Артем Волков',
        'date': '30 октября 2025',
        'rating': 5,
        'text': 'Заказывал PS5 Slim с доставкой на дом. Все привезли быстро, аккуратно упаковано. Приставка работает отлично!',
        'avatar': 'А',
        'likes': 27,
    },
{
        'id': 5,
        'name': 'Иван Петров',
        'date': '27 октября 2025',
        'rating': 5,
        'text': 'Отличный магазин! Купил PS5 Pro и очень доволен. Ребята все объяснили, помогли с выбором игр, настроили приставку прямо в магазине.',
        'avatar': 'И',
        'likes': 24,
    },
    {
        'id': 6,
        'name': 'Алена Смирнова',
        'date': '28 октября 2025',
        'rating': 5,
        'text': 'Брала PS4 в подарок сыну на день рождения. Консультанты очень дружелюбные, посоветовали хорошие игры для ребенка.',
        'avatar': 'А',
        'likes': 18,
    },
    {
        'id': 7,
        'name': 'Дарья Козлова',
        'date': '29 октября 2025',
        'rating': 5,
        'text': 'Лучший магазин PlayStation в городе! Покупала геймпад DualSense. Цены адекватные, все оригинальное.',
        'avatar': 'Д',
        'likes': 31,
    },
    {
        'id': 8,
        'name': 'Артем Волков',
        'date': '30 октября 2025',
        'rating': 5,
        'text': 'Заказывал PS5 Slim с доставкой на дом. Все привезли быстро, аккуратно упаковано. Приставка работает отлично!',
        'avatar': 'А',
        'likes': 27,
    },
]




def catalog(request):
    #Первая загрузка каталога — только 4 карточки
    context = {
        'page': 'catalog',
        'title': 'Каталог товаров — LetsPlay',
        'products': PRODUCTS[:6],  # первые 4
        'show_button': len(PRODUCTS) > 6,
        'categories': [
            {'id': 'all', 'name': 'Все товары'},
            {'id': 'consoles', 'name': 'Приставки'},
            {'id': 'accessories', 'name': 'Аксессуары'},
            {'id': 'subscriptions', 'name': 'Подписки'},
        ]
    }
    return render(request, 'main/catalog.html', context)


def load_more_products(request):

    #AJAX-запрос для кнопки 'Показать ещё'
    offset = bounded_int(request.GET.get('offset'), 0, 100000)
    print("🔍 load_more_products вызван, offset =", offset)
    limit = 6
    products = PRODUCTS[offset:offset + limit]
    return JsonResponse({'products': products})




from main.models import Review

def reviews(request):
    reviews = Review.objects.all().order_by('-date')  # по дате, самые свежие наверху
    return render(request, 'main/reviews.html', {'reviews': reviews})


def reviews(request):
    #Основная страница отзывов
    limit = 4  # по 4 карточки при загрузке
    context = {
        'page': 'reviews',
        'title': 'Отзывы клиентов — LetsPlay',
        'reviews': reviews_list[:limit],
        'show_button': len(reviews_list) > limit,
        'stats': {
            'total_clients': '1900+',
            'rating': '4.9 / 5.0',
            'recommendations': '98%',
        },
    }
    return render(request, 'main/reviews.html', context)



def load_more_reviews(request):
    #AJAX-запрос для кнопки 'Показать ещё отзывы'
    offset = bounded_int(request.GET.get('offset'), 0, 100000)
    print("🔍 load_more_products вызван, offset =", offset)
    limit = 4
    next_reviews = reviews_list[offset:offset + limit]
    return JsonResponse({'reviews': next_reviews})"""
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, Http404

"""def catalog_detail(request, product_id):
    # ищем товар по id в списке PRODUCTS
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        raise Http404("Товар не найден")
    return render(request, 'main/catalog_detail.html', {'product': product})


from django.shortcuts import render, get_object_or_404
from .models import Product


def catalog(request):
    products = Product.objects.all()
    return render(request, 'main/catalog.html', {'products': products})
def catalog_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return redirect(product.get_absolute_url(), permanent=True)
"""

from django.shortcuts import render, get_object_or_404
from .models import Product, Review




from django.db.models import Q
# вверху файла это уже, кажется, есть, но пусть будет напоминание

def catalog(request):
    category = request.GET.get('category', None)

    categories_map = {
        'consoles': 'Приставки',
        'accessories': 'Аксессуары',
        'subscriptions': 'Подписки',
        'disks': 'Диски',
    }

    filter_map = {
        'consoles': ['ps5', 'ps4', 'xbox'],
        'accessories': [],
        'disks': ['ps5', 'ps4', 'xbox'],
        'subscriptions': ['deluxe', 'extra', 'essential', 'ea play'],
    }

    active_category = category if category else 'all'

    # Берём только активные товары
    qs = Product.objects.filter(is_active=True).exclude(slug__isnull=True).exclude(slug='').select_related('category')

    # Фильтр по категории
    if active_category != 'all':
        qs = qs.filter(category__category_type=active_category)

    # Подфильтр (платформа / тип подписки)
    active_filter = (request.GET.get('filter') or '').lower()
    if active_filter not in filter_map.get(active_category, []):
        active_filter = ''
    if active_filter:
        qs = qs.filter(
            Q(platform=active_filter) |
            Q(subscription_type=active_filter)
        )

    active_condition = request.GET.get('condition', '')
    if active_condition not in ('new', 'used') or active_category not in ('consoles', 'disks'):
        active_condition = ''
    active_firmware = request.GET.get('firmware', '')
    if active_firmware not in ('stock', 'modified') or active_category != 'consoles' or active_filter != 'ps4':
        active_firmware = ''
    if active_condition:
        qs = qs.filter(condition=active_condition)
    if active_firmware:
        qs = qs.filter(firmware_status=active_firmware)

    from decimal import Decimal, InvalidOperation
    max_price = ''
    try:
        candidate = Decimal(request.GET.get('max_price', ''))
        if candidate.is_finite() and 0 < candidate <= 10000000:
            max_price = format(candidate, 'f')
            qs = qs.filter(price__lte=candidate)
    except (InvalidOperation, ValueError):
        pass

    # Сначала сортируем так, чтобы "главный" вариант группы был первым
    qs = qs.order_by('variant_group', 'variant_order', 'id')

    # Теперь "сжимаем":
    # - если variant_group пустой → показываем как есть
    # - если не пустой → только первый товар в группе
    unique_products = []
    seen_groups = set()

    for p in qs:
        if p.variant_group:
            group_key = (p.variant_group, p.condition, p.firmware_status, p.platform)
            if group_key in seen_groups:
                continue
            seen_groups.add(group_key)
            unique_products.append(p)
        else:
            unique_products.append(p)

    context = {
        "products": unique_products,
        "active_category": active_category,
        "filters": filter_map.get(active_category, []) if active_category != 'all' else [],
        "active_filter": active_filter,
        "active_condition": active_condition,
        "max_price": max_price,
        "active_firmware": active_firmware,
        "categories": categories_map,
    }

    return render(request, "main/catalog.html", context)





def catalog_detail(request, product_id):
    """Детальная страница по старому ID (оставляем для обратной совместимости)"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return redirect(product.get_absolute_url(), permanent=True)

from django.shortcuts import render, get_object_or_404
from .models import Product, Review

from django.db.models import Avg

from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from .models import Product, Review

def catalog_detail_by_slug(request, slug):
    """Детальная страница товара по slug"""

    product = get_object_or_404(Product.objects.select_related('category'), slug=slug, is_active=True)

    enriched_product = product.get_enriched_data()
    gallery = product.images.all()

    # Похожие товары
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    # Отзывы
    reviews = Review.objects.filter(is_approved=True).order_by('-date')

    # 🔥 ВАЖНО: подбираем варианты по variant_group
    variants = []
    if product.variant_group:
        variants = Product.objects.filter(
            variant_group=product.variant_group,
            is_active=True
        ).order_by('variant_order', 'id')

    return render(request, 'main/catalog_detail.html', {
        'product': product,
        'enriched_product': enriched_product,
        'product_json_ld': product_schema(product),
        'gallery': gallery,
        'related_products': related_products,
        'reviews': reviews,
        'variants': variants,   # ← тут ПЕРЕДАЁМ
        'page': 'catalog_detail',
        'title': f"{product.name} — LetsPlay Екатеринбург",
    })



from django.db.models import Avg

import json
from django.utils import timezone
from main.services.reviews_stats import get_reviews_stats

def review_count_label(count):
    last_two = count % 100
    if 11 <= last_two <= 14:
        word = 'отзывов'
    elif count % 10 == 1:
        word = 'отзыв'
    elif 2 <= count % 10 <= 4:
        word = 'отзыва'
    else:
        word = 'отзывов'
    return f'{count} {word}'

def reviews(request):
    limit = 4
    qs = Review.objects.filter(is_approved=True, is_generated=False).order_by('-date', '-id')
    stats = get_reviews_stats()
    return render(request, 'main/reviews.html', {
        'reviews': qs[:limit], 'stats': stats,
        'review_count_label': review_count_label(stats['total_clients']),
        'show_button': qs.count() > limit, 'page': 'reviews',
    })

def bounded_int(value, default, maximum):
    try:
        return max(0, min(int(value), maximum))
    except (ValueError, TypeError):
        return default


def load_more_products(request):
    offset = bounded_int(request.GET.get('offset'), 0, 100000)
    limit = 6
    products = Product.objects.filter(is_active=True).select_related('category').order_by('id')[offset:offset + limit]
    data = [p.get_enriched_data() for p in products]
    return JsonResponse({'products': data})


from django.http import JsonResponse
from .models import Review

LOAD_MORE_LIMIT = 8

def load_more_reviews(request):
    offset = bounded_int(request.GET.get('offset'), 0, 100000)
    limit = max(1, bounded_int(request.GET.get('limit'), LOAD_MORE_LIMIT, 24))

    qs_all = Review.objects.filter(is_approved=True, is_generated=False).order_by('-date', '-id')
    qs = qs_all[offset:offset + limit]

    reviews = []
    for r in qs:
        reviews.append({
            'id': r.id,
            'name': r.name,
            'avatar': r.avatar,  # если у тебя уже хранится буква
            'date': r.date.strftime("%d.%m.%Y"),
            'rating': r.rating,
            'text': r.text,
            'likes': r.likes,
        })

    next_offset = offset + len(reviews)
    has_more = next_offset < qs_all.count()

    return JsonResponse({
        'reviews': reviews,
        'next_offset': next_offset,
        'has_more': has_more,
    })






from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Product
from .models import Cart, CartItem


def get_cart(request):
    """Возвращает или создаёт корзину"""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


# views.py
from .models import Cart, CartItem, Product




from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('/')
    return render(request, 'main/register.html')




from .models import Order

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cart





from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
import json

@require_POST
def update_cart_item(request, item_id):
    """
    Обновление количества товара в корзине:
    - если AJAX (каталог) → ждём JSON {"delta": +/-1} и отвечаем JSON
    - если обычная форма (страница корзины) → используем POST-поля и делаем redirect
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        try:
            data = json.loads(request.body.decode('utf-8'))
            delta = data.get('delta') if isinstance(data, dict) else None
            if type(delta) is not int or delta not in (-1, 1):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            return JsonResponse({'error': 'Передайте delta: 1 или -1.'}, status=400)
        quantity = cart_item.quantity + delta
    else:
        action = request.POST.get('action')
        if action in ('increase', 'decrease'):
            quantity = cart_item.quantity + (1 if action == 'increase' else -1)
        elif action == 'set':
            try:
                quantity = int(request.POST.get('quantity', ''))
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Некорректное количество.'}, status=400)
        else:
            return JsonResponse({'error': 'Неизвестное действие.'}, status=400)

    if quantity > 999:
        return JsonResponse({'error': 'Максимальное количество — 999.'}, status=400)
    if quantity > cart_item.quantity and (not cart_item.product.is_active or not cart_item.product.in_stock):
        if is_ajax:
            return JsonResponse({'error': 'Товар недоступен для заказа.'}, status=409)
        messages.error(request, 'Товар недоступен для заказа. Его можно удалить из корзины.')
        return redirect('main:cart_view')
    if quantity <= 0:
        cart_item.delete()
        quantity = 0
    else:
        cart_item.quantity = quantity
        cart_item.save(update_fields=['quantity'])
    if is_ajax:
        return JsonResponse({'quantity': quantity})

    return redirect('letsplay:cart_view')



@require_POST
def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    product_name = cart_item.product.name
    cart_item.delete()

    messages.success(request, f'{product_name} удален из корзины')

    # Если это AJAX-запрос, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product_name} удален из корзины',
            'cart_total_items': cart.get_total_items(),
            'cart_total_price': float(cart.get_total_price()),
        })

    return redirect('letsplay:cart_view')


@require_POST
def clear_cart(request):
    """Очистка корзины"""
    cart = get_or_create_cart(request)
    cart.clear()

    messages.success(request, 'Корзина очищена')

    # Если это AJAX-запрос, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Корзина очищена',
        })

    return redirect('letsplay:cart_view')


# ==================== API для получения корзины (JSON) ====================

def cart_data_api(request):
    """API для получения данных корзины в формате JSON"""
    cart = get_or_create_cart(request)

    return JsonResponse(cart.to_dict())


# ==================== Оформление заказа ====================

from django.db import transaction
from .services.notifications import notify_about_new_order_async


def checkout_view(request):
    """Страница оформления заказа"""
    cart = get_or_create_cart(request)

    # City pricing is not activated yet: never price another store's order
    # using the legacy Ekaterinburg Product.price values.
    if not cart.store_id or cart.store.slug != 'ekaterinburg':
        messages.error(request, 'Онлайн-заказы этого магазина пока недоступны. Свяжитесь с магазином для оформления.')
        return redirect('main:cart_view')

    if cart.get_total_items() == 0:
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('letsplay:catalog')

    from .checkout_forms import CheckoutForm
    checkout_form = CheckoutForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and checkout_form.is_valid():
        data = checkout_form.cleaned_data
        name, email, phone = data['name'], data['email'], data['phone']
        delivery_method, address = data['delivery_method'], data['address']
        payment_method, comment = data['payment_method'], data['comment']

        with transaction.atomic():
            # Use one snapshot for validation, totals and saved order rows.
            Cart.objects.select_for_update().get(pk=cart.pk)
            cart_items = list(cart.items.select_for_update().select_related('product', 'product__category'))
            if not cart_items:
                messages.warning(request, 'Ваша корзина пуста')
                return redirect('main:catalog')
            if any(not item.product.is_active or not item.product.in_stock or item.quantity < 1 for item in cart_items):
                messages.error(request, 'Наличие одного из товаров изменилось. Проверьте корзину.')
                return redirect('main:cart_view')
            order = Order.objects.create(
                store=cart.store,
                store_name=cart.store.name,
                user=request.user if request.user.is_authenticated else None,
                customer_name=name,
                customer_email=email,
                customer_phone=phone,
                delivery_method=delivery_method,
                delivery_address=address,
                payment_method=payment_method,
                total_price=sum(item.product.price * item.quantity for item in cart_items),
                comment=comment,
            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    selection_summary=cart_item.product.get_selection_summary(),
                    product_price=cart_item.product.price,
                    quantity=cart_item.quantity,
                )

            cart.clear()

        if not request.user.is_authenticated:
            guest_order_ids = request.session.get('guest_order_ids', [])
            request.session['guest_order_ids'] = [*guest_order_ids, order.pk]

        # запускаем письма уже ПОСЛЕ успешной записи в БД
        transaction.on_commit(lambda: notify_about_new_order_async(order.id))

        messages.success(request, f'Заказ №{order.id} успешно оформлен! Мы свяжемся с вами в ближайшее время.')
        return redirect('letsplay:order_success', order_id=order.id)

    context = {
        'checkout_form': checkout_form,
        'entered': request.POST if request.method == 'POST' else {},
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'total_price': cart.get_total_price(),
        'total_items': cart.get_total_items(),
    }

    return render(request, 'main/checkout.html', context)



def _get_accessible_order(request, order_id):
    """A numeric order ID is not authorization to read customer details."""
    allowed = Q(user__isnull=True, pk__in=request.session.get('guest_order_ids', []))
    if request.user.is_authenticated:
        allowed |= Q(user_id=request.user.pk)
    return get_object_or_404(Order.objects.filter(allowed), pk=order_id)


@never_cache
def order_success_view(request, order_id):
    """Страница успешного оформления заказа"""
    order = _get_accessible_order(request, order_id)

    context = {
        'order': order,
    }

    return render(request, 'main/order_success.html', context)


# ==================== Личный кабинет - заказы ====================
from django.contrib.auth.decorators import login_required

@login_required(login_url='letsplay:login')
def my_orders_view(request):
    # Загружаем заказы текущего пользователя
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')

    context = {
        'user': request.user,
        'orders': orders
    }
    return render(request, 'main/my_orders.html', context)


@never_cache
def order_detail_view(request, order_id):
    """Order details belong to the account owner or checkout session."""
    order = _get_accessible_order(request, order_id)

    context = {
        'order': order,
    }

    return render(request, 'main/order_detail.html', context)

from django.shortcuts import render


def get_or_create_cart(request):
    """Получает или создает корзину для текущего пользователя/сессии"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Для анонимных пользователей используем session_key
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)

    if not cart.store_id:
        store = Store.objects.get(slug='ekaterinburg')
        Cart.objects.filter(pk=cart.pk, store__isnull=True).update(store=store)
        cart.refresh_from_db(fields=['store'])
    return cart
def cart_view(request):
    """Страница корзины"""
    cart = get_or_create_cart(request)

    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'total_price': cart.get_total_price(),
        'total_items': cart.get_total_items(),
    }

    return render(request, 'main/cart.html', context)



from django.shortcuts import render



def csrf_failure(request, reason=""):
    return render(request, "main/csrf_error.html", {"reason": reason}, status=403)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Review
from .forms import ReviewForm


from django.contrib import messages
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import Review
from .forms import ReviewForm


def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.date = timezone.now().date()
            review.save()
            # ✅ Добавляем уведомление
            messages.success(request, 'Ваш отзыв отправлен на модерацию и появится после проверки администратором.')
            return redirect('letsplay:reviews')
        else:
            messages.error(request, 'Пожалуйста, заполните все поля корректно.')
    else:
        form = ReviewForm()
    return render(request, 'main/submit_review.html', {'form': form})




def auth_page_view(request):
    return render(request, 'main/auth.html')


from django.http import JsonResponse
from .models import Review
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
def like_review(request, review_id):
    if request.method != "POST":
        return JsonResponse({'success': False}, status=405)

    review = get_object_or_404(Review, id=review_id)

    liked_reviews = request.session.get('liked_reviews', [])

    if review_id in liked_reviews:
        review.likes = max(review.likes - 1, 0)
        liked_reviews.remove(review_id)
        liked = False
    else:
        review.likes += 1
        liked_reviews.append(review_id)
        liked = True

    review.save()
    request.session['liked_reviews'] = liked_reviews

    return JsonResponse({
        'success': True,
        'liked': liked,
        'likes': review.likes
    })


import json
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Cart, CartItem

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Cart, CartItem
import json

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True, in_stock=True)

    # корзина по юзеру или по сессии
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)

    # базовое количество - 1
    quantity = 1

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        if cart_item.quantity >= 999:
            return JsonResponse({'error': 'Максимальное количество — 999.'}, status=400)
        cart_item.quantity += quantity
        cart_item.save()

    # количество уникальных позиций
    cart_count = cart.items.count()

    # обязательно JSON, чтобы фронт смог распарсить
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "ok": True,
            "product_id": product.id,
            "item_id": cart_item.id,
            "quantity": cart_item.quantity,
            "cart_count": cart_count,
        })

    # на всякий случай fallback при обычном POST
    return redirect("letsplay:cart_view")







def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        cart = Cart.objects.filter(session_key=session_key).first() if session_key else None

    count = cart.items.count() if cart else 0
    return JsonResponse({"count": count})



def get_cart_item(request, product_id):
    # ищем корзину так же, как в add_to_cart / cart_count
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        if not request.session.session_key:
            return JsonResponse({"exists": False})
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    if not cart:
        return JsonResponse({"exists": False})

    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        return JsonResponse({
            "exists": True,
            "item_id": cart_item.id,
            "quantity": cart_item.quantity
        })
    except CartItem.DoesNotExist:
        return JsonResponse({"exists": False})

def privacy_policy(request):
    return render(request, "main/privacy_policy.html")




from django.shortcuts import render

# ...

def service_gifts(request):
    return render(request, "main/service_gifts.html", {
        "page": "home",
    })


def service_console_selection(request):
    return render(request, "main/service_console_selection.html", {
        "page": "home",
    })


def service_setup(request):
    return render(request, "main/service_setup.html", {
        "page": "home",
    })


def delivery_page(request):
    return render(request, "main/delivery.html", {
        "page": "home",
    })


def warranty_page(request):
    return render(request, "main/warranty.html", {
        "page": "home",
    })


def support_page(request):
    return render(request, "main/support.html", {
        "page": "home",
    })







