# Подробная инструкция по установке LetsPlay на Django

## Шаг 1: Подготовка Django проекта

### 1.1 Создайте Django проект (если еще не создан)
```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте его
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите Django
pip install django pillow

# Создайте проект
django-admin startproject config .

# Создайте приложение
python manage.py startapp letsplay
```

### 1.2 Добавьте приложение в settings.py
```python
# config/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'letsplay',  # добавьте это
]
```

## Шаг 2: Скопируйте файлы из django-export

### 2.1 Структура папок
Создайте следующую структуру в вашем Django проекте:

```
your_project/
├── config/
│   ├── settings.py
│   └── urls.py
├── letsplay/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       ← скопируйте из django-export/static/css/
│   │   ├── js/
│   │   │   └── main.js         ← скопируйте из django-export/static/js/
│   │   └── images/             ← создайте папку и добавьте изображения
│   ├── templates/
│   │   ├── base.html           ← скопируйте из django-export/templates/
│   │   ├── home.html           ← скопируйте из django-export/templates/
│   │   ├── about.html          ← скопируйте из django-export/templates/
│   │   ├── catalog.html        ← скопируйте из django-export/templates/
│   │   └── reviews.html        ← скопируйте из django-export/templates/
│   ├── views.py                ← замените содержимое файлом из django-export/
│   ├── urls.py                 ← создайте и скопируйте из django-export/
│   └── models.py
└── manage.py
```

### 2.2 Команды копирования

**Windows (PowerShell):**
```powershell
# Создайте необходимые папки
mkdir letsplay\static\css, letsplay\static\js, letsplay\static\images, letsplay\templates

# Скопируйте файлы
copy django-export\static\css\style.css letsplay\static\css\
copy django-export\static\js\main.js letsplay\static\js\
copy django-export\templates\*.html letsplay\templates\
copy django-export\views.py letsplay\views.py
copy django-export\urls.py letsplay\urls.py
```

**Linux/Mac:**
```bash
# Создайте необходимые папки
mkdir -p letsplay/static/{css,js,images} letsplay/templates

# Скопируйте файлы
cp django-export/static/css/style.css letsplay/static/css/
cp django-export/static/js/main.js letsplay/static/js/
cp django-export/templates/*.html letsplay/templates/
cp django-export/views.py letsplay/views.py
cp django-export/urls.py letsplay/urls.py
```

## Шаг 3: Настройка Django

### 3.1 Обновите config/settings.py

```python
# config/settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ... существующие настройки ...

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'letsplay' / 'static',
]

# Media files (uploaded by users)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'letsplay' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
            ],
        },
    },
]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Yekaterinburg'  # Екатеринбург
USE_I18N = True
USE_TZ = True
```

### 3.2 Обновите config/urls.py

```python
# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('letsplay.urls', namespace='letsplay')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Шаг 4: Добавление изображений

### 4.1 Временные изображения-заглушки
Поместите изображения товаров в `letsplay/static/images/`:

- `ps5-pro.jpg` - PlayStation 5 Pro
- `ps5-slim.jpg` - PlayStation 5 Slim
- `ps4-pro.jpg` - PlayStation 4 Pro
- `dualsense.jpg` - Контроллер DualSense
- `psvr2.jpg` - PlayStation VR2

### 4.2 Где взять изображения

1. **Unsplash** (бесплатно): https://unsplash.com/s/photos/playstation
2. **Pexels** (бесплатно): https://www.pexels.com/search/playstation/
3. **Ваши собственные фотографии** товаров
4. **Официальные изображения Sony** (с соблюдением авторских прав)

## Шаг 5: Создание базы данных и миграции

```bash
# Создайте миграции
python manage.py makemigrations

# Примените миграции
python manage.py migrate

# Создайте суперпользователя для админ-панели
python manage.py createsuperuser
```

## Шаг 6: Запуск сервера разработки

```bash
# Соберите статические файлы
python manage.py collectstatic --noinput

# Запустите сервер
python manage.py runserver
```

Откройте браузер и перейдите по адресу: **http://127.0.0.1:8000/**

## Шаг 7: Проверка работы

Убедитесь, что работают все страницы:
- Главная: http://127.0.0.1:8000/
- О нас: http://127.0.0.1:8000/about/
- Каталог: http://127.0.0.1:8000/catalog/
- Отзывы: http://127.0.0.1:8000/reviews/

## Дополнительные настройки

### Создание моделей для товаров (опционально)

Если хотите хранить товары в базе данных, создайте модели:

```python
# letsplay/models.py

from django.db import models

class Category(models.Model):
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('Slug', unique=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField('Название', max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    old_price = models.DecimalField('Старая цена', max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField('Изображение', upload_to='products/', null=True, blank=True)
    badge = models.CharField('Бейдж', max_length=50, blank=True)
    description = models.TextField('Описание', blank=True)
    features = models.JSONField('Характеристики', default=list)
    rating = models.IntegerField('Рейтинг', default=5)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class Review(models.Model):
    name = models.CharField('Имя', max_length=100)
    text = models.TextField('Текст отзыва')
    rating = models.IntegerField('Оценка', default=5)
    date = models.DateField('Дата', auto_now_add=True)
    likes = models.IntegerField('Лайки', default=0)
    is_active = models.BooleanField('Опубликован', default=True)
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.name} - {self.rating}/5"
```

После создания моделей:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Регистрация моделей в админ-панели

```python
# letsplay/admin.py

from django.contrib import admin
from .models import Category, Product, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'rating', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_active']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'date', 'likes', 'is_active']
    list_filter = ['rating', 'is_active', 'date']
    search_fields = ['name', 'text']
    list_editable = ['is_active']
```

## Решение проблем

### Проблема: Статические файлы не загружаются
**Решение:**
```bash
python manage.py collectstatic --clear
python manage.py collectstatic --noinput
```

### Проблема: Изображения не отображаются
**Решение:**
1. Проверьте пути в settings.py
2. Убедитесь, что изображения находятся в `letsplay/static/images/`
3. Проверьте правильность путей в views.py

### Проблема: 404 ошибка на страницах
**Решение:**
1. Проверьте правильность URL в config/urls.py
2. Убедитесь, что namespace='letsplay' указан
3. Проверьте, что letsplay/urls.py существует и подключен

### Проблема: Стили не применяются
**Решение:**
1. Очистите кэш браузера (Ctrl+Shift+Del)
2. Проверьте консоль браузера на ошибки
3. Убедитесь, что {% load static %} есть в шаблонах

## Что дальше?

1. **Добавьте реальные изображения** товаров
2. **Создайте модели** для товаров и отзывов
3. **Добавьте формы** для обратной связи
4. **Интегрируйте платежную систему** (ЮKassa, CloudPayments)
5. **Добавьте корзину** покупок
6. **Настройте email** уведомления
7. **Оптимизируйте SEO** (мета-теги, sitemap)
8. **Добавьте SSL сертификат** для продакшена
9. **Настройте nginx** и gunicorn для деплоя
10. **Создайте систему учета** заказов

## Поддержка

Если возникнут вопросы, проверьте:
- Документацию Django: https://docs.djangoproject.com/
- Django Girls Tutorial: https://tutorial.djangogirls.org/ru/
- Stack Overflow: https://stackoverflow.com/questions/tagged/django

Удачи с вашим проектом LetsPlay! 🎮
