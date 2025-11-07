# Структура проекта LetsPlay Django

## Рекомендуемая структура вашего Django проекта

```
letsplay_project/                    # Корневая папка проекта
│
├── config/                          # Настройки Django проекта
│   ├── __init__.py
│   ├── settings.py                 # Основные настройки
│   ├── urls.py                     # Главный маршрутизатор
│   ├── wsgi.py
│   └── asgi.py
│
├── letsplay/                        # Основное приложение
│   ├── migrations/                 # Миграции базы данных
│   │   └── __init__.py
│   │
│   ├── static/                     # Статические файлы
│   │   ├── css/
│   │   │   └── style.css          # ← Скопировать из django-export/
│   │   ├── js/
│   │   │   └── main.js            # ← Скопировать из django-export/
│   │   └── images/                # Изображения товаров
│   │       ├── ps5-pro.jpg
│   │       ├── ps5-slim.jpg
│   │       ├── ps4-pro.jpg
│   │       ├── dualsense.jpg
│   │       └── psvr2.jpg
│   │
│   ├── templates/                  # HTML шаблоны
│   │   ├── base.html              # ← Скопировать из django-export/
│   │   ├── home.html              # ← Скопировать из django-export/
│   │   ├── about.html             # ← Скопировать из django-export/
│   │   ├── catalog.html           # ← Скопировать из django-export/
│   │   └── reviews.html           # ← Скопировать из django-export/
│   │
│   ├── __init__.py
│   ├── admin.py                    # Админ-панель
│   ├── apps.py
│   ├── models.py                   # Модели базы данных (опционально)
│   ├── urls.py                     # ← Скопировать из django-export/
│   ├── views.py                    # ← Скопировать из django-export/
│   └── tests.py
│
├── media/                          # Файлы, загруженные пользователями
│   └── products/                   # Изображения товаров из админки
│
├── staticfiles/                    # Собранные статические файлы (создается автоматически)
│
├── venv/                           # Виртуальное окружение Python
│
├── .gitignore                      # Файлы, игнорируемые Git
├── requirements.txt                # Зависимости Python
├── manage.py                       # Django CLI
└── README.md                       # Документация проекта
```

## Что находится в каждой папке

### `/config/` - Настройки проекта
- **settings.py** - Основные настройки (БД, статика, приложения)
- **urls.py** - Главный роутер, подключает URL-ы приложений
- **wsgi.py/asgi.py** - Для запуска на продакшен сервере

### `/letsplay/` - Основное приложение

#### `/static/` - Статические файлы
```
static/
├── css/
│   └── style.css          # Все стили сайта (48 KB)
│                          # - Цветовая палитра
│                          # - Анимированный градиентный фон
│                          # - Стили для всех компонентов
│                          # - Адаптивность
│
├── js/
│   └── main.js            # JavaScript функциональность (5 KB)
│                          # - Мобильное меню
│                          # - Фильтры каталога
│                          # - Анимации при скролле
│                          # - Утилиты
│
└── images/                # Изображения товаров
    ├── ps5-pro.jpg       # PlayStation 5 Pro
    ├── ps5-slim.jpg      # PlayStation 5 Slim
    ├── ps4-pro.jpg       # PlayStation 4 Pro
    ├── dualsense.jpg     # Контроллер DualSense
    └── psvr2.jpg         # PlayStation VR2
```

#### `/templates/` - HTML шаблоны
```
templates/
├── base.html              # Базовый шаблон (8 KB)
│   ├── <head> с мета-тегами и подключением CSS
│   ├── Анимированный градиентный фон
│   ├── Header с навигацией
│   ├── {% block content %}
│   ├── Footer
│   └── Подключение JavaScript
│
├── home.html              # Главная страница (10 KB)
│   ├── Hero секция с выбором консолей
│   ├── Статистика (4 карточки)
│   ├── Преимущества (6 карточек)
│   └── CTA секция
│
├── about.html             # Страница "О нас" (8 KB)
│   ├── Информация о компании
│   ├── Миссия
│   ├── Преимущества (4 карточки)
│   ├── Команда (2 человека)
│   └── Ассортимент
│
├── catalog.html           # Каталог (7 KB)
│   ├── Фильтры категорий
│   ├── Сетка товаров (6 карточек)
│   └── JavaScript для фильтрации
│
└── reviews.html           # Отзывы (6 KB)
    ├── Баннер статистики
    ├── Сетка отзывов (4 отзыва)
    └── CTA для новых отзывов
```

#### Основные файлы приложения
- **views.py** - Логика страниц (5 views)
  - `home()` - Главная
  - `about()` - О нас
  - `catalog()` - Каталог с данными товаров
  - `reviews()` - Отзывы с данными отзывов
  
- **urls.py** - Маршруты приложения
  ```python
  urlpatterns = [
      path('', views.home, name='home'),
      path('about/', views.about, name='about'),
      path('catalog/', views.catalog, name='catalog'),
      path('reviews/', views.reviews, name='reviews'),
  ]
  ```

- **models.py** - Модели БД (опционально)
  - Category - Категории товаров
  - Product - Товары
  - Review - Отзывы

- **admin.py** - Настройка админ-панели

## Размеры файлов

| Файл | Размер | Описание |
|------|--------|----------|
| style.css | ~48 KB | Все стили сайта |
| main.js | ~5 KB | JavaScript функциональность |
| base.html | ~8 KB | Базовый шаблон |
| home.html | ~10 KB | Главная страница |
| about.html | ~8 KB | О нас |
| catalog.html | ~7 KB | Каталог |
| reviews.html | ~6 KB | Отзывы |
| views.py | ~5 KB | Django views |
| **ИТОГО** | **~97 KB** | Весь код проекта |

## Файлы для копирования

### Из `django-export/` копируйте:

1. **Обязательные файлы:**
   - `static/css/style.css` → `letsplay/static/css/`
   - `static/js/main.js` → `letsplay/static/js/`
   - `templates/*.html` → `letsplay/templates/`
   - `views.py` → `letsplay/`
   - `urls.py` → `letsplay/`

2. **Документация (опционально):**
   - `README.md` - Общее описание
   - `INSTALLATION.md` - Подробная инструкция
   - `QUICK_START.md` - Быстрый старт
   - `STRUCTURE.md` - Этот файл

## Файлы для .gitignore

```gitignore
# Python
*.pyc
__pycache__/
*.py[cod]
*$py.class

# Django
db.sqlite3
media/
staticfiles/
*.log

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## requirements.txt

```txt
Django>=4.2,<5.0
Pillow>=10.0.0
```

## Команды для создания структуры

### Linux/Mac:
```bash
mkdir -p letsplay/static/{css,js,images}
mkdir -p letsplay/templates
mkdir -p letsplay/migrations
mkdir -p media/products
touch letsplay/{__init__,admin,apps,models,urls,views,tests}.py
```

### Windows (PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path letsplay\static\css, letsplay\static\js, letsplay\static\images, letsplay\templates, letsplay\migrations, media\products
New-Item -ItemType File -Path letsplay\__init__.py, letsplay\admin.py, letsplay\apps.py, letsplay\models.py, letsplay\urls.py, letsplay\views.py, letsplay\tests.py
```

## Следующие шаги

1. ✅ Создайте структуру папок
2. ✅ Скопируйте файлы из django-export/
3. ✅ Настройте settings.py и urls.py
4. ✅ Добавьте изображения в static/images/
5. ✅ Запустите migrate и runserver
6. ⬜ Создайте модели (опционально)
7. ⬜ Настройте админ-панель
8. ⬜ Добавьте формы обратной связи
9. ⬜ Интегрируйте платежную систему
10. ⬜ Деплой на продакшен

---

**Готово!** Теперь у вас есть полная структура проекта Django для LetsPlay! 🎮
