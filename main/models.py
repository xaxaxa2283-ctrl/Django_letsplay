"""from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('consoles', 'Consoles'),
        ('accessories', 'Accessories'),
        ('subscriptions', 'Subscriptions'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/')  # фото будут храниться в media/products/
    badge = models.CharField(max_length=50, null=True, blank=True)
    features = models.JSONField(default=list, blank=True)  # список характеристик
    rating = models.IntegerField(default=5)

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Каталог"



class Review(models.Model):
    name = models.CharField(max_length=100)        # Имя клиента
    date = models.DateField()                      # Дата отзыва
    rating = models.IntegerField(default=5)       # Рейтинг (1–5)
    text = models.TextField()                      # Текст отзыва
    avatar = models.CharField(max_length=1, blank=True, null=True)  # Первая буква или иконка
    likes = models.IntegerField(default=0)        # Кол-во лайков

    def __str__(self):
        return f"{self.name} ({self.date})"""

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Категории товаров"""
    CATEGORY_CHOICES = [
        ('consoles', 'Приставки'),
        ('accessories', 'Аксессуары'),
        ('subscriptions', 'Подписки'),
    ]

    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', blank=True, null=True)  # временно
    category_type = models.CharField('Тип', max_length=50, choices=CATEGORY_CHOICES)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Модель товара (объединённая версия)"""
    PLATFORM_CHOICES = [
        ('ps4', 'PlayStation 4'),
        ('ps5', 'PlayStation 5'),
        ('xbox', 'Xbox'),
        ('universal', 'Универсальный'),
    ]

    SUBSCRIPTION_TYPE_CHOICES = [
        ('essential', 'Plus Essential'),
        ('extra', 'Plus Extra'),
        ('deluxe', 'Plus Deluxe'),
    ]

    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL',unique=True, blank=True, null=True)  # убрали unique
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория'
    )

    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    old_price = models.DecimalField('Старая цена', max_digits=10, decimal_places=2, null=True, blank=True)

    image = models.ImageField('Изображение', upload_to='products/', null=True, blank=True)
    image_url = models.URLField('URL изображения', null=True, blank=True,
                                help_text='Используется если нет загруженного изображения')

    badge = models.CharField('Значок', max_length=50, blank=True)
    features = models.JSONField('Особенности', default=list, blank=True,null=True)
    specifications = models.JSONField('Характеристики', default=list, blank=True,null=True)
    rating = models.IntegerField('Рейтинг', default=5, choices=[(i, i) for i in range(1, 6)])
    in_stock = models.BooleanField('В наличии', default=True)
    description = models.TextField('Описание', blank=True, null=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    is_active = models.BooleanField('Активен', default=True)

    variant_group = models.CharField(
        'Группа вариантов',
        max_length=50,
        blank=True,
        null=True,
        help_text='Например: dualsense-ps5, ps-plus-deluxe'
    )
    variant_name = models.CharField(
        'Название варианта',
        max_length=50,
        blank=True,
        null=True,
        help_text='Например: Белый, Чёрный, 1 месяц, 3 месяца, 12 месяцев'
    )
    variant_order = models.IntegerField(
        'Порядок варианта',
        default=0,
    help_text = 'Для сортировки вариантов (0,1,2...)'
    )

    # 👇 НОВОЕ поле
    variant_color = models.CharField(
        'Цвет варианта',
        max_length=7,
        blank=True,
        null=True,
        help_text='HEX-цвет, например: #ffffff, #000000, #1e90ff'
    )
    platform = models.CharField(
        'Платформа',
        max_length=20,
        choices=PLATFORM_CHOICES,
        blank=True,
        null=True,
        help_text="Платформа для консолей и аксессуаров"
    )
    subscription_type = models.CharField(
        'Тип подписки',
        max_length=20,
        choices=SUBSCRIPTION_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text="Тип подписки PlayStation Plus"
    )
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Каталог'
        ordering = ['-created_at']
        models.Index(fields=['platform']),  # Новый индекс
        models.Index(fields=['subscription_type']),  # Новый индекс

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/catalog/product/{self.slug}/'

    def get_image_url(self):
        """Возвращает URL изображения"""
        if self.image:
            return self.image.url
        return self.image_url or ''

    def get_discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((1 - float(self.price) / float(self.old_price)) * 100)
        return 0

    def get_category_name(self):
        return self.category.get_category_type_display()

    def get_default_description(self):
        descriptions = {
            'consoles': 'Современная игровая консоль нового поколения с улучшенной графикой, высокой производительностью и обширной библиотекой игр. В комплекте уже более 700 игр!',
            'accessories': 'Качественный аксессуар для PlayStation, который улучшает игровой опыт. Совместим со всеми моделями PlayStation.',
            'subscriptions': 'Подписка PlayStation Plus открывает доступ к онлайн-мультиплееру, каталогам игр и бонусам.',
        }
        return descriptions.get(self.category.category_type,
                                'Качественный товар от PlayStation с официальной гарантией.')

    def get_default_specifications(self):
        specs = {
            'consoles': [
                {'label': 'Производитель', 'value': 'Sony'},
                {'label': 'Гарантия', 'value': '1 год'},
                {'label': 'Страна производства', 'value': 'Япония'},
            ],
            'accessories': [
                {'label': 'Производитель', 'value': 'Sony'},
                {'label': 'Совместимость', 'value': 'PS4/PS5'},
            ],
            'subscriptions': [
                {'label': 'Тип', 'value': 'Цифровой код'},
                {'label': 'Срок действия', 'value': '12 месяцев'},
            ],
        }
        return specs.get(self.category.category_type, [])

    def get_enriched_data(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'category': self.category.category_type,
            'category_name': self.get_category_name(),
            'price': float(self.price),
            'old_price': float(self.old_price) if self.old_price else None,
            'image': self.get_image_url(),
            'badge': self.badge,
            'features': self.features or [],
            'rating': self.rating,
            'description': self.description or self.get_default_description(),
            'specifications': self.specifications or self.get_default_specifications(),
            'in_stock': self.in_stock,
            'discount_percent': self.get_discount_percent(),
        }


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField('Изображение', upload_to='products/gallery/')
    order = models.IntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['order']

    def __str__(self):
        return f'{self.product.name} - Изображение {self.order}'


class Review(models.Model):
    """Отзывы клиентов"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField('Имя', max_length=100)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    rating = models.IntegerField('Рейтинг', default=5)
    text = models.TextField('Текст')
    avatar = models.CharField('Аватар', max_length=1, blank=True, null=True)
    likes = models.IntegerField('Лайки', default=0)
    is_approved = models.BooleanField('Одобрен', default=False)
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} ({self.date})"







# cart_models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Cart(models.Model):
    """Корзина покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Пользователь',
        related_name='carts'
    )
    session_key = models.CharField(
        'Ключ сессии',
        max_length=40,
        null=True,
        blank=True,
        help_text='Для анонимных пользователей'
    )
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-updated_at']

    def __str__(self):
        if self.user:
            return f'Корзина {self.user.username}'
        return f'Корзина (сессия {self.session_key})'

    def get_total_price(self):
        """Возвращает общую стоимость корзины"""
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        """Возвращает общее количество товаров"""
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        """Очищает корзину"""
        self.items.all().delete()

    def to_dict(self):
        """Возвращает данные корзины в виде словаря"""
        return {
            'id': self.id,
            'items': [item.to_dict() for item in self.items.all()],
            'total_price': float(self.get_total_price()),
            'total_items': self.get_total_items(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class CartItem(models.Model):
    """Товар в корзине"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Корзина'
    )
    product = models.ForeignKey(
        'Product',  # Ссылка на модель Product из models.py
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)
    added_at = models.DateTimeField('Добавлен', auto_now_add=True)

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = [['cart', 'product']]
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'

    def get_total_price(self):
        """Возвращает общую стоимость товара"""
        return self.product.price * self.quantity

    def increase_quantity(self, amount=1):
        """Увеличивает количество"""
        self.quantity += amount
        self.save()

    def decrease_quantity(self, amount=1):
        """Уменьшает количество"""
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
        else:
            self.delete()

    def to_dict(self):
        """Возвращает данные товара в виде словаря"""
        return {
            'id': self.id,
            'product': self.product.get_enriched_data(),
            'quantity': self.quantity,
            'total_price': float(self.get_total_price()),
            'added_at': self.added_at.isoformat(),
        }


class Order(models.Model):
    """Заказ"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('confirmed', 'Подтверждён'),
        ('processing', 'Обрабатывается'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Наличные при получении'),
        ('card', 'Банковская карта'),
        ('online', 'Онлайн-оплата'),
    ]

    DELIVERY_CHOICES = [
        ('pickup', 'Самовывоз'),
        ('courier', 'Курьер'),
        ('post', 'Почта России'),
    ]

    # Пользователь
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Пользователь',
        related_name='orders'
    )

    # Контактная информация
    customer_name = models.CharField('Имя', max_length=200)
    customer_email = models.EmailField('Email')
    customer_phone = models.CharField('Телефон', max_length=20)

    # Адрес доставки
    delivery_method = models.CharField('Способ доставки', max_length=20, choices=DELIVERY_CHOICES)
    delivery_address = models.TextField('Адрес доставки', blank=True)

    # Оплата
    payment_method = models.CharField('Способ оплаты', max_length=20, choices=PAYMENT_CHOICES)

    # Стоимость
    total_price = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2)

    # Статус
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')

    # Комментарий
    comment = models.TextField('Комментарий', blank=True)

    # Служебные поля
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ №{self.id} от {self.created_at.strftime("%d.%m.%Y")}'

    def get_status_display_color(self):
        """Возвращает цвет для статуса"""
        colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'processing': 'primary',
            'shipped': 'info',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return colors.get(self.status, 'secondary')


class OrderItem(models.Model):
    """Товар в заказе"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Товар'
    )

    # Сохраняем данные на момент заказа
    product_name = models.CharField('Название товара', max_length=200)
    product_price = models.DecimalField('Цена товара', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество')

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f'{self.product_name} x{self.quantity}'

    def get_total_price(self):
        """Возвращает общую стоимость товара"""
        return self.product_price * self.quantity




# models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Доп. данные пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'Профиль {self.user.username}'




#новая глава catalog_detail
from django.db.models.signals import post_save
from django.dispatch import receiver
from .services.notifications import send_order_created_email

"""
@receiver(post_save, sender=Order)
def order_created_notification(sender, instance, created, **kwargs):
    if created:
        send_order_created_email(instance)"""


from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

from .services.notifications import (
    send_order_created_email,
    send_order_confirmation_email,
)

logger = logging.getLogger(__name__)





