from django import forms
from django.contrib import admin
from django.contrib import admin
from django.utils.html import format_html

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
    features = forms.JSONField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'style': 'font-family: monospace;'}),
        help_text='Введите список особенностей: ["HDR", "Ray tracing"]'
    )

    specifications = forms.JSONField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 6, 'style': 'font-family: monospace;'}),
        help_text='Введите характеристики: [{"label": "Память", "value": "1 ТБ"}]'
    )

    class Meta:
        model = Product
        fields = '__all__'


# ======================================
#              PRODUCT
# ======================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

    list_display = [
        'name', 'category', 'platform', 'subscription_type',
        'price', 'old_price',
        'rating', 'in_stock', 'is_active', 'badge',
        'variant_group', 'variant_name', 'variant_order',
    ]

    list_filter = [
        'category',
        'platform',
        'subscription_type',
        'rating',
        'in_stock',
        'is_active',
        'variant_group',
    ]
    search_fields = ['name', 'description', 'variant_group', 'variant_name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'in_stock', 'is_active']

    inlines = [ProductImageInline]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name', 'slug', 'category',
                'platform', 'subscription_type',
                'badge'
            )
        }),
        # 👇 НОВЫЙ БЛОК ДЛЯ ВАРИАНТОВ
        ('Варианты товара', {
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
            'fields': ('rating', 'in_stock', 'is_active')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    class Media:
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

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'rating', 'is_approved')
    list_filter = ('is_approved', 'date')
    search_fields = ('name', 'text')


# ======================================
#            ORDER ITEMS INLINE
# ======================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'get_total_price']
    can_delete = False

    def get_total_price(self, obj):
        if not obj or obj.price is None or obj.quantity is None:
            return 0
        return obj.price * obj.quantity

    get_total_price.short_description = "Сумма"


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



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_name', 'customer_phone', 'customer_email',
        'delivery_method', 'payment_method', 'total_price',
        'created_at', 'colored_status'
    ]

    list_filter = ['status', 'delivery_method', 'payment_method', 'created_at']
    search_fields = ['id', 'customer_name', 'customer_email', 'customer_phone']

    readonly_fields = ['total_price', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Информация о клиенте', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Доставка и оплата', {
            'fields': ('delivery_method', 'delivery_address', 'payment_method')
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
