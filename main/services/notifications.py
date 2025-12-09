# main/services/notifications.py
from threading import Thread
import logging

from django.conf import settings
from django.core.mail import send_mail, get_connection
from main.models import Order  # путь подгони, если другой

logger = logging.getLogger(__name__)

def send_order_created_email(order):
    subject = f"Новый заказ №{order.id} — LetsPlay"

    items_text = ""
    for item in order.items.all():
        items_text += (
            f"- {item.product_name} × {item.quantity} шт. "
            f"= {item.get_total_price()} ₽\n"
        )

    admin_link = f"https://letsplayekb.shop/admin/main/order/{order.id}/change/"

    message = (
        f"🛒 НОВЫЙ ЗАКАЗ №{order.id}\n\n"
        f"Имя: {order.customer_name}\n"
        f"Телефон: {order.customer_phone}\n"
        f"Email: {order.customer_email}\n\n"
        f"Доставка: {order.get_delivery_method_display()}\n"
        f"Адрес: {order.delivery_address or '—'}\n"
        f"Оплата: {order.get_payment_method_display()}\n\n"
        f"Товары:\n{items_text}\n"
        f"Итого: {order.total_price} ₽\n\n"
        f"Комментарий: {order.comment or '—'}\n\n"
        f"Админка: {admin_link}"
    )

    # короткий таймаут, чтобы не висеть минуту
    connection = get_connection(timeout=5)

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ORDER_NOTIFICATION_EMAIL],
        fail_silently=True,  # чтобы не падать даже внутри try
        connection=connection,
    )



def send_order_confirmation_email(order):
    """Письмо клиенту: подтверждение оформления заказа."""
    if not order.customer_email:
        return  # на всякий случай

    subject = f"Ваш заказ №{order.id} в LetsPlay принят"

    items_text = ""
    for item in order.items.all():
        items_text += (
            f"- {item.product_name} × {item.quantity} шт. "
            f"= {item.get_total_price()} ₽\n"
        )

    message = (
        f"{order.customer_name}, добрый день!\n\n"
        f"Спасибо за заказ в магазине LetsPlay 🎮\n\n"
        f"Номер вашего заказа: №{order.id}\n"
        f"Сумма: {order.total_price} ₽\n\n"
        f"Состав заказа:\n{items_text}\n"
        f"Способ доставки: {order.get_delivery_method_display()}\n"
        f"Адрес доставки: {order.delivery_address or 'самовывоз'}\n"
        f"Способ оплаты: {order.get_payment_method_display()}\n\n"
        f"Мы свяжемся с вами для уточнения деталей.\n\n"
        f"Если вы не оформляли этот заказ, просто проигнорируйте это письмо."
    )

    connection = get_connection(timeout=5)

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.customer_email],
        fail_silently=True,
        connection=connection,
    )


def notify_about_new_order_async(order_id: int):
    """
    Запускает отправку писем в отдельном потоке, чтобы не тормозить ответ пользователю.
    """

    def _job():
        try:
            order = Order.objects.prefetch_related("items").get(pk=order_id)
        except Order.DoesNotExist:
            return

        try:
            send_order_created_email(order)
        except Exception:
            logger.exception("Ошибка при отправке письма продавцу о новом заказе")

        try:
            send_order_confirmation_email(order)
        except Exception:
            logger.exception("Ошибка при отправке письма клиенту о новом заказе")

    Thread(target=_job, daemon=True).start()













