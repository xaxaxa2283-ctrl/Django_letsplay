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
from django.db.models import Sum, F
import json


from .models import Cart, CartItem, Order, OrderItem
def home(request):
    #Главная страница
    context = {
        'page': 'home',
        'title': 'LetsPlay — Магазин PlayStation в Екатеринбурге'
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
    offset = int(request.GET.get('offset', 0))
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
    offset = int(request.GET.get('offset', 0))
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
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'main/catalog_detail.html', {'product': product})
"""

from django.shortcuts import render, get_object_or_404
from .models import Product, Review

def catalog(request):
    """Каталог товаров с фильтрацией по категориям"""
    # Получаем выбранную категорию из GET-параметров (?category=consoles)
    category_param = request.GET.get('category', 'all')
    print("catalog: category_param =", category_param)
    # Все категории для отображения кнопок
    categories = Category.objects.all()

    # Фильтрация товаров по категории
    if category_param != 'all':
        products = Product.objects.filter(category__category_type=category_param)
    else:
        products = Product.objects.all()
    print("catalog: products count =", products.count())
    context = {
        'page': 'catalog',
        'title': 'Каталог товаров — LetsPlay',
        'categories': categories,
        'products': products,
        'current_category': category_param,
    }

    return render(request, 'main/catalog.html', context)
def catalog_detail(request, product_id):
    """Детальная страница по старому ID (оставляем для обратной совместимости)"""
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'main/catalog_detail.html', {'product': product})

from django.shortcuts import render, get_object_or_404
from .models import Product, Review

def catalog_detail_by_slug(request, slug):
    """Детальная страница товара по slug"""

    product = get_object_or_404(Product, slug=slug)
    print("Я тут")
    print(product.get_enriched_data())

    # "Обогащённые" данные из метода модели
    enriched_product = product.get_enriched_data()

    # Галерея дополнительных изображений
    gallery = product.images.all()

    # Похожие товары (в той же категории, кроме текущего)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]

    # Отзывы об этом товаре
    reviews = Review.objects.filter(is_approved=True).order_by('-date')


    return render(request, 'main/catalog_detail.html', {
        'product': product,
        'enriched_product': enriched_product,
        'gallery': gallery,
        'related_products': related_products,
        'reviews': reviews,
        'page': 'catalog_detail',
        'title': f"{product.name} — LetsPlay Екатеринбург",
    })


from django.db.models import Avg

def reviews(request):
    limit = 4

    reviews = Review.objects.filter(is_approved=True).order_by('-date')[:limit]

    stats = {
        'total_clients': Review.objects.filter(is_approved=True).count(),
        'rating': round(
            Review.objects.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0, 1
        ),
        'recommendations': 98,  # Или то, что нужно
    }

    return render(request, 'main/reviews.html', {
        'reviews': reviews,
        'stats': stats,
        'show_button': Review.objects.filter(is_approved=True).count() > limit,
    })



def load_more_products(request):
    offset = int(request.GET.get('offset', 0))
    limit = 6
    products = Product.objects.all()[offset:offset + limit]
    data = [p.get_enriched_data() for p in products]
    return JsonResponse({'products': data})


def load_more_reviews(request):
    offset = int(request.GET.get('offset', 0))
    limit = 4

    qs = Review.objects.filter(is_approved=True).order_by('-date')[offset:offset + limit]

    reviews = []
    for r in qs:
        reviews.append({
            'id': r.id,
            'name': r.name,
            'avatar': r.avatar,
            'date': r.date.strftime("%d.%m.%Y"),
            'rating': r.rating,
            'text': r.text,
            'likes': r.likes,
        })

    return JsonResponse({'reviews': reviews})






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


@require_POST
def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request)

    # Получаем количество из POST или устанавливаем 1
    quantity = int(request.POST.get('quantity', 1))

    # Проверяем, есть ли товар в корзине
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        # Если товар уже есть, увеличиваем количество
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'{product.name} добавлен в корзину ({cart_item.quantity} шт.)')
    else:
        messages.success(request, f'{product.name} добавлен в корзину')

    # Если это AJAX-запрос, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} добавлен в корзину',
            'cart_total_items': cart.get_total_items(),
            'cart_total_price': float(cart.get_total_price()),
        })

    # Иначе редирект на страницу корзины
    return redirect('letsplay:cart_view')


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


def checkout(request):
    """Оформление заказа"""
    cart_id = request.session.get('cart_id')
    items = []
    total = 0

    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id)
            items = cart.items.all()
            total = sum(item.product.price * item.quantity for item in items)
        except Cart.DoesNotExist:
            messages.error(request, "Корзина не найдена.")
            return redirect('letsplay:catalog')
    else:
        messages.error(request, "Корзина пуста.")
        return redirect('letsplay:catalog')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # 💾 Здесь позже добавим сохранение заказа в БД
        messages.success(request, f"Спасибо, {full_name}! Ваш заказ принят.")

        # Очистим корзину после оформления
        cart.items.all().delete()
        request.session.pop('cart_id', None)

        return redirect('letsplay:checkout_success')

    return render(request, 'main/checkout.html', {
        'items': items,
        'total': total
    })


def checkout_success(request):
    """Страница успешного оформления заказа"""
    return render(request, 'main/checkout_success.html')


@require_POST
def update_cart_item(request, item_id):
    """Обновление количества товара в корзине"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    action = request.POST.get('action')

    if action == 'increase':
        cart_item.increase_quantity()
        messages.success(request, 'Количество увеличено')
    elif action == 'decrease':
        cart_item.decrease_quantity()
        messages.success(request, 'Количество уменьшено')
    elif action == 'set':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()

    # Если это AJAX-запрос, возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total_items': cart.get_total_items(),
            'cart_total_price': float(cart.get_total_price()),
            'item_total_price': float(cart_item.get_total_price()) if cart_item.id else 0,
        })

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

def checkout_view(request):
    """Страница оформления заказа"""
    cart = get_or_create_cart(request)

    if cart.get_total_items() == 0:
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('letsplay:catalog')






    if request.method == 'POST':
        # Обработка формы заказа
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=request.POST.get('name'),
            customer_email=request.POST.get('email'),
            customer_phone=request.POST.get('phone'),
            delivery_method=request.POST.get('delivery_method'),
            delivery_address=request.POST.get('address', ''),
            payment_method=request.POST.get('payment_method'),
            total_price=cart.get_total_price(),
            comment=request.POST.get('comment', ''),
        )

        # Создаем товары заказа
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity,
            )
        #new block


        # Очищаем корзину
        cart.clear()

        messages.success(request, f'Заказ №{order.id} успешно оформлен! Мы свяжемся с вами в ближайшее время.')
        return redirect('letsplay:order_success', order_id=order.id)

    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
        'total_price': cart.get_total_price(),
        'total_items': cart.get_total_items(),
    }

    return render(request, 'main/checkout.html', context)


def order_success_view(request, order_id):
    """Страница успешного оформления заказа"""
    order = get_object_or_404(Order, id=order_id)

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


def order_detail_view(request, order_id):
    """Детальная информация о заказе"""
    order = get_object_or_404(Order, id=order_id)

    # Проверка доступа
    if not request.user.is_authenticated or (order.user and order.user != request.user):
        messages.error(request, 'У вас нет доступа к этому заказу')
        return redirect('catalog')

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
    return render(request, "main/csrf_error.html", {"reason": reason})


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




