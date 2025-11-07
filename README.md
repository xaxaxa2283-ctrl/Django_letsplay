# Экспорт LetsPlay в Django

Это руководство поможет вам перенести React-приложение LetsPlay в Django проект.

## Структура Django проекта

```
your_django_project/
├── letsplay/                      # Django app
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css         # Общий CSS файл
│   │   ├── js/
│   │   │   └── main.js           # Общий JavaScript файл
│   │   └── images/
│   ├── templates/
│   │   ├── base.html             # Базовый шаблон
│   │   ├── home.html             # Главная страница
│   │   ├── about.html            # О нас
│   │   ├── catalog.html          # Каталог
│   │   └── reviews.html          # Отзывы
│   ├── views.py
│   ├── urls.py
│   └── models.py
└── config/
    ├── settings.py
    └── urls.py
```

## Шаги для переноса

### 1. Скопируйте файлы

Из этой папки `django-export/` скопируйте:
- `templates/` → в вашу Django app папку `templates/`
- `static/css/style.css` → в `static/css/`
- `static/js/main.js` → в `static/js/`

### 2. Настройте Django settings.py

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "letsplay/static",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'letsplay/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

### 3. Создайте views.py

Используйте пример из `django-export/views.py`

### 4. Настройте URLs

Используйте пример из `django-export/urls.py`

### 5. Соберите статические файлы

```bash
python manage.py collectstatic
```

## Отличия от React версии

1. **Навигация**: Вместо JavaScript роутинга используются обычные Django URLs
2. **Интерактивность**: Базовая интерактивность реализована на vanilla JavaScript
3. **Стили**: Tailwind CSS конвертирован в обычный CSS
4. **Анимации**: Простые CSS анимации вместо Motion/React

## Дополнительные возможности

Для добавления:
- **AJAX фильтры каталога**: Используйте fetch() в main.js
- **Форма отзывов**: Создайте Django Form
- **Корзина покупок**: Используйте Django sessions
- **Оплата**: Интегрируйте платежную систему (ЮKassa, CloudPayments)

## Зависимости

Рекомендуется установить:
```bash
pip install django pillow
```

Для работы с изображениями товаров.
