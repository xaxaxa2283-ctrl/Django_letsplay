# Быстрый старт - Перенос LetsPlay в Django

## 📋 Что нужно сделать

### 1. Скопируйте файлы из папки `django-export/`

```
django-export/
├── static/
│   ├── css/style.css         → letsplay/static/css/
│   └── js/main.js            → letsplay/static/js/
├── templates/
│   ├── base.html             → letsplay/templates/
│   ├── home.html             → letsplay/templates/
│   ├── about.html            → letsplay/templates/
│   ├── catalog.html          → letsplay/templates/
│   └── reviews.html          → letsplay/templates/
├── views.py                  → letsplay/views.py
└── urls.py                   → letsplay/urls.py
```

### 2. Настройте Django

**config/settings.py:**
```python
INSTALLED_APPS = [
    ...
    'letsplay',
]

TEMPLATES = [{
    'DIRS': [BASE_DIR / 'letsplay' / 'templates'],
    ...
}]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'letsplay' / 'static']

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Yekaterinburg'
```

**config/urls.py:**
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('letsplay.urls', namespace='letsplay')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 3. Добавьте изображения

Поместите изображения товаров в `letsplay/static/images/`:
- ps5-pro.jpg
- ps5-slim.jpg
- ps4-pro.jpg
- dualsense.jpg
- psvr2.jpg

### 4. Запустите проект

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

Откройте: http://127.0.0.1:8000/

## ✅ Что получится

- ✅ Главная страница с героем, статистикой, преимуществами
- ✅ Страница "О нас" с информацией о компании и команде
- ✅ Каталог с фильтрацией товаров по категориям
- ✅ Страница отзывов с отзывами клиентов
- ✅ Адаптивный дизайн для мобильных устройств
- ✅ Анимации и интерактивность на JavaScript
- ✅ Современный дизайн в вашей цветовой палитре

## 📝 Основные отличия от React версии

| React | Django |
|-------|--------|
| Компоненты | HTML шаблоны |
| useState/useEffect | Django views + vanilla JS |
| React Router | Django URLs |
| Tailwind CSS | Обычный CSS |
| Motion/React | CSS анимации + Intersection Observer |

## 🎯 Что можно добавить дальше

1. **База данных товаров** - создайте модели Product, Category
2. **Корзина покупок** - используйте Django sessions
3. **Оплата** - интегрируйте ЮKassa или CloudPayments
4. **Форма заказа** - Django Forms
5. **Email уведомления** - Django Email Backend
6. **Админ-панель** - настройте Django Admin
7. **API** - Django REST Framework для мобильного приложения

## 📚 Полезные ссылки

- Подробная инструкция: `INSTALLATION.md`
- Основной README: `README.md`
- Django документация: https://docs.djangoproject.com/

## 💡 Совет

Начните с простого - используйте данные из views.py (списки словарей).
Когда все заработает, переходите к созданию моделей и работе с базой данных.

---

**Нужна помощь?** Откройте `INSTALLATION.md` для подробных инструкций!
