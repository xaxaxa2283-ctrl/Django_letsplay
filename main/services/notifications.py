from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def send_order_created_email(order):
    subject = f"Новый заказ №{order.id} — LetsPlay"

    # Формируем список товаров
    items_text = ""
    for item in order.items.all():
        items_text += (
            f"- {item.product_name} × {item.quantity} шт. "
            f"= {item.get_total_price()} ₽\n"
        )

    admin_link = f"https://letsplayekb.shop/admin/main/order/{order.id}/change/"

    message = (
        f"🛒 НОВЫЙ ЗАКАЗ №{order.id}\n\n"
        f"👤 Клиент: {order.customer_name}\n"
        f"📞 Телефон: {order.customer_phone}\n"
        f"📧 Email: {order.customer_email}\n\n"
        f"🚚 Способ доставки: {order.get_delivery_method_display()}\n"
        f"🏠 Адрес: {order.delivery_address or '—'}\n"
        f"💳 Способ оплаты: {order.get_payment_method_display()}\n\n"
        f"📦 Товары:\n{items_text}\n"
        f"💰 Итого: {order.total_price} ₽\n\n"
        f"💬 Комментарий: {order.comment or '—'}\n\n"
        f"🔗 Открыть заказ в админке:\n{admin_link}"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ORDER_NOTIFICATION_EMAIL],
        fail_silently=False,
    )
