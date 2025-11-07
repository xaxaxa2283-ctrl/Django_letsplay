# letsplay/views.py

from django.shortcuts import render

def home(request):
    """Главная страница"""
    context = {
        'page': 'home',
        'title': 'LetsPlay — Магазин PlayStation в Екатеринбурге'
    }
    return render(request, 'main/home.html', context)

def about(request):
    """Страница О нас"""
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

def catalog(request):
    """Каталог товаров"""
    # В реальном проекте данные будут из БД
    products = [
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
            'name': 'PS Plus Premium 12 месяцев',
            'category': 'subscriptions',
            'price': 7499,
            'features': ['Онлайн игры', 'Каталог игр', 'Классика PS'],
            'rating': 5,
        },
        {
            'id': 8,
            'name': 'PS Plus Premium 12 месяцев',
            'category': 'subscriptions',
            'price': 7499,
            'features': ['Онлайн игры', 'Каталог игр', 'Классика PS'],
            'rating': 5,
        },
    ]
    
    context = {
        'page': 'catalog',
        'title': 'Каталог товаров — LetsPlay',
        'products': products,
        'categories': [
            {'id': 'all', 'name': 'Все товары'},
            {'id': 'consoles', 'name': 'Приставки'},
            {'id': 'accessories', 'name': 'Аксессуары'},
            {'id': 'subscriptions', 'name': 'Подписки'},
        ]
    }
    return render(request, 'main/catalog.html', context)

def reviews(request):
    """Страница отзывов"""
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
    ]
    
    context = {
        'page': 'reviews',
        'title': 'Отзывы клиентов — LetsPlay',
        'reviews': reviews_list,
        'stats': {
            'total_clients': '1900+',
            'rating': '4.9 / 5.0',
            'recommendations': '98%'
        }
    }
    return render(request, 'main/reviews.html', context)
