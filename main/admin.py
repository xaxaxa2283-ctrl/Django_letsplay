from .admin_readiness import product_readiness, store_readiness, offer_readiness
from .admin_fields import FeatureLinesField, SpecificationField, CategoryTypeSelect
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib import admin
from django.utils.html import format_html
from .models import Store, StoreOffer


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'address', 'phone', 'readiness']
    readonly_fields = ['readiness']

    @admin.display(description='Проверка данных')
    def readiness(self, obj):
        return store_readiness(obj)
    search_fields = ['name', 'city', 'address']
    prepopulated_fields = {'slug': ('city',)}
    fieldsets = (
        ('Магазин', {'fields': ('name', 'slug', 'city', 'address', 'phone', 'opening_hours', 'readiness')}),
        ('Будущее подключение МоегоСклада', {
            'description': 'Сопоставление для будущей интеграции. Синхронизация пока не выполняется. Пароли и токены здесь не сохраняются.',
            'fields': ('moysklad_warehouse_id', 'moysklad_price_type_id'),
        }),
    )


@admin.register(StoreOffer)
class StoreOfferAdmin(admin.ModelAdmin):
    list_display = ['product', 'store', 'price', 'availability', 'updated_at', 'readiness']
    list_select_related = ['product', 'store']

    @admin.display(description='Проверка предложения')
    def readiness(self, obj):
        return offer_readiness(obj)
    list_filter = ['store', 'availability']
    search_fields = ['product__name', 'store__city']
    autocomplete_fields = ['product', 'store']
    readonly_fields = ['updated_at', 'readiness']
    fieldsets = (('Подготовка предложений по городам', {
        'description': 'Эти данные пока не подключены к витрине и корзине. Действующие цены сайта меняются в разделе «Товары». Предложения Екатеринбурга скопированы один раз; автоматической синхронизации пока нет.',
        'fields': ('store', 'product', 'price', 'availability', 'updated_at', 'readiness'),
    }),)

from .models import Order, OrderItem, Product, ProductImage, Category, Review
# остальное как у тебя

from .models import (
    Product, ProductImage, Category,
    Review, Order, OrderItem
)

# ======================================
#              CATEGORY
# ======================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'slug']
    list_filter = ['category_type']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


# ======================================
#         PRODUCT IMAGES INLINE
# ======================================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'order']


# ======================================
#          PRODUCT ADMIN FORM
# ======================================

class ProductAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        category_widget = CategoryTypeSelect(choices=self.fields['category'].choices)
        if hasattr(self.fields['category'].widget, 'widget'):
            self.fields['category'].widget.widget = category_widget
        else:
            self.fields['category'].widget = category_widget
        self.fields['variant_group'].help_text = 'Одинаковый код связывает версии одной модели. Например: ps5-slim. Для самостоятельного товара оставьте пустым.'
        self.fields['variant_name'].help_text = 'Краткое отличие версии: «1 ТБ, с дисководом». Состояние и прошивка указываются отдельно.'
        self.fields['condition'].help_text = 'Для приставок и дисков. Неизвестное состояние оставьте пустым.'
        self.fields['firmware_status'].help_text = 'Только для приставок PS4. Если данных нет, оставьте пустым.'

    def clean(self):
        data = super().clean()
        category = data.get('category')
        if category:
            if category.category_type not in ('consoles', 'disks'):
                data['condition'] = ''
            if category.category_type != 'consoles' or data.get('platform') != 'ps4':
                data['firmware_status'] = ''
            if category.category_type != 'subscriptions':
                data['subscription_type'] = ''
        return data

    # Recovered catalog images use local static URLs. Normalize these existing
    # paths to the storefront URL before ModelForm runs URLField validation.
    image_url = forms.CharField(required=False, label='URL изображения')

    def clean_image_url(self):
        value = self.cleaned_data.get('image_url', '').strip()
        if value.startswith(('/static/', '/media/')) and not any(c in value for c in ('\\', '?', '#')):
            from urllib.parse import urlsplit
            if '..' not in urlsplit(value).path.split('/'):
                value = settings.PUBLIC_SITE_URL.rstrip('/') + value
        if value:
            from django.core.validators import URLValidator
            URLValidator(schemes=['http', 'https'])(value)
        return value

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError('Цена не может быть отрицательной.')
        return price

    features = FeatureLinesField(required=False, label='Особенности', help_text='Одна особенность на строку. Например: второй контроллер в комплекте.')
    specifications = SpecificationField(required=False, label='Характеристики', help_text='Добавьте пары названия и значения. Комплектацию можно указать отдельной характеристикой.')

    class Meta:
        model = Product
        fields = '__all__'


# ======================================
#              PRODUCT
# ======================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_select_related = ['category']

    @admin.display(description='Проверка карточки')
    def readiness(self, obj):
        return product_readiness(obj)

    list_display = [
        'name', 'category', 'platform', 'subscription_type',
        'condition', 'firmware_status', 'price', 'old_price',
        'rating', 'in_stock', 'is_active', 'badge', 'readiness',
        'variant_group', 'variant_name', 'variant_order',
    ]

    list_filter = [
        'category',
        'platform',
        'subscription_type',
        'condition',
        'firmware_status',
        'rating',
        'in_stock',
        'is_active',
        'variant_group',
    ]
    search_fields = ['name', 'description', 'variant_group', 'variant_name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'in_stock', 'is_active']

    inlines = [ProductImageInline]
    readonly_fields = ['created_at', 'updated_at', 'readiness']

    fieldsets = (
        ('Основная информация', {
            'description': 'Сначала выберите категорию и платформу. При сохранении неприменимые состояние, прошивка и тип подписки очищаются.',
            'fields': (
                'name', 'slug', 'category',
                'platform', 'subscription_type',
                'condition', 'firmware_status',
                'badge'
            )
        }),
        # 👇 НОВЫЙ БЛОК ДЛЯ ВАРИАНТОВ
        ('Варианты товара', {
            'description': 'Одна позиция — одна конфигурация с собственной ценой и наличием. Не создавайте позиции для каждого экземпляра б/у. Свяжите версии общим кодом группы.',
            'fields': ('variant_group', 'variant_name', 'variant_order', 'variant_color'),
        }),
        ('Цены', {
            'fields': ('price', 'old_price')
        }),
        ('Изображения', {
            'fields': ('image', 'image_url')
        }),
        ('Описание', {
            'fields': ('description', 'features', 'specifications')
        }),
        ('Статус', {
            'fields': ('rating', 'in_stock', 'is_active', 'readiness')
        }),
        ('Связь с МоимСкладом', {
            'description': 'Укажите ID товара или модификации после пробной проверки подключения. Токен API здесь не хранится.',
            'fields': ('moysklad_assortment_id',),
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    class Media:
        js = ('admin/js/product_context.js',)
        css = {
            'all': ('admin/css/custom_admin.css',)
        }



# ======================================
#            PRODUCT IMAGES
# ======================================

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'order', 'image']
    list_filter = ['product']
    list_editable = ['order']


# ======================================
#              REVIEWS
# ======================================
from django.db.models import F
from django.contrib import admin


@admin.action(description="✅ Одобрить выбранные отзывы")
def approve_reviews(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description="⛔ Снять одобрение у выбранных отзывов")
def unapprove_reviews(modeladmin, request, queryset):
    queryset.update(is_approved=False)


@admin.action(description="📌 Закрепить выбранные отзывы")
def pin_reviews(modeladmin, request, queryset):
    queryset.update(is_pinned=True)


@admin.action(description="📍 Открепить выбранные отзывы")
def unpin_reviews(modeladmin, request, queryset):
    queryset.update(is_pinned=False)


@admin.action(description="👍 Добавить +10 лайков")
def add_10_likes(modeladmin, request, queryset):
    queryset.update(likes=F("likes") + 10)


@admin.action(description="🔄 Сбросить лайки")
def reset_likes(modeladmin, request, queryset):
    queryset.update(likes=0)


@admin.action(description="🔤 Заполнить аватар первой буквой имени")
def fill_avatar(modeladmin, request, queryset):
    updated = 0
    for r in queryset:
        if not r.avatar and r.name:
            r.avatar = r.name.strip()[:1].upper()
            r.save(update_fields=["avatar"])
            updated += 1
    modeladmin.message_user(request, f"Обновлено аватаров: {updated}")

from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rating', 'likes', 'is_approved', 'is_pinned', 'date')
    list_filter = ('is_approved', 'is_pinned', 'rating')
    search_fields = ('name', 'text')
    list_editable = ('is_approved', 'is_pinned')  # ✅ можно переключать прямо в списке
    ordering = ('-is_pinned', '-date')
    readonly_fields = ('date',)
    actions = [
        approve_reviews,
        unapprove_reviews,
        pin_reviews,
        unpin_reviews,
        add_10_likes,
        reset_likes,
        fill_avatar,
    ]
    fieldsets = (
        ("Основное", {
            "fields": ("name", "text", "rating", "avatar", "likes")
        }),
        ("Публикация", {
            "fields": ("is_approved", "is_pinned")
        }),
        ("Служебное", {
            "fields": ("date", "product")
        }),
    )
# ======================================
#            ORDER ITEMS INLINE
# ======================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'selection_summary', 'product_price', 'quantity', 'get_total_price']
    can_delete = False

    def get_total_price(self, obj):
        if not obj or obj.product_price is None or obj.quantity is None:
            return 0
        return obj.product_price * obj.quantity

    get_total_price.short_description = "Сумма"

    def has_add_permission(self, request, obj=None):
        return False


# ======================================
#                 ORDERS
# ======================================


# ====== действия для смены статуса заказа ======

@admin.action(description='Статус: Ожидает обработки')
def set_status_pending(modeladmin, request, queryset):
    queryset.update(status='pending')


@admin.action(description='Статус: Подтверждён')
def set_status_confirmed(modeladmin, request, queryset):
    queryset.update(status='confirmed')


@admin.action(description='Статус: Обрабатывается')
def set_status_processing(modeladmin, request, queryset):
    queryset.update(status='processing')


@admin.action(description='Статус: Отправлен')
def set_status_shipped(modeladmin, request, queryset):
    queryset.update(status='shipped')


@admin.action(description='Статус: Доставлен')
def set_status_delivered(modeladmin, request, queryset):
    queryset.update(status='delivered')


@admin.action(description='Статус: Отменён')
def set_status_cancelled(modeladmin, request, queryset):
    queryset.update(status='cancelled')



class OrderAdminForm(forms.ModelForm):
    customer_email = forms.EmailField(required=False, label='Email')

    class Meta:
        model = Order
        fields = '__all__'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm

    list_display = [
        'id', 'store', 'customer_name', 'customer_phone', 'customer_email',
        'delivery_method', 'payment_method', 'total_price',
        'created_at', 'colored_status'
    ]

    list_filter = ['store', 'status', 'delivery_method', 'payment_method', 'created_at']
    search_fields = ['id', 'customer_name', 'customer_email', 'customer_phone']

    readonly_fields = ['store', 'store_name', 'total_price', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Информация о клиенте', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Доставка и оплата', {
            'fields': ('store', 'store_name', 'delivery_method', 'delivery_address', 'payment_method')
        }),
        ('Состав заказа', {
            'fields': ('total_price',)
        }),
        ('Статус', {
            'fields': ('status',)
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = [
        set_status_pending,
        set_status_confirmed,
        set_status_processing,
        set_status_shipped,
        set_status_delivered,
        set_status_cancelled,
    ]

    @admin.display(description="Статус", ordering="status")
    def colored_status(self, obj):
        colors = {
            'pending': '#ff9800',  # Ожидает
            'confirmed': '#00bcd4',  # Подтверждён
            'processing': '#3f51b5',  # Обрабатывается
            'shipped': '#2196f3',  # Отправлен
            'delivered': '#4caf50',  # Доставлен
            'cancelled': '#f44336',  # Отменён
        }

        color = colors.get(obj.status, '#9e9e9e')
        label = obj.get_status_display()

        return format_html(
            '<span style="color: white; background:{}; padding:4px 10px; border-radius:6px; font-size:12px;">{}</span>',
            color,
            label
        )
