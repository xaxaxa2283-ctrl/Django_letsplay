# main/services/telegram_notifications.py
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_order_notification(order):
    """
    Отправка уведомления в Telegram о новом заказе (продавцу/админу).
    """
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    chat_id = getattr(settings, "TELEGRAM_ADMIN_CHAT_ID", None)

    if not token or not chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN or TELEGRAM_ADMIN_CHAT_ID not set, skip telegram notify")
        return

    # Собираем текст сообщения
    lines = [
        f"🆕 НОВЫЙ ЗАКАЗ №{order.id}",
        "",
        f"👤 {order.customer_name}",
        f"📞 {order.customer_phone}",
    ]

    if order.customer_email:
        lines.append(f"📧 {order.customer_email}")

    lines.extend([
        "",
        f"🚚 Доставка: {order.get_delivery_method_display()}",
    ])

    if order.delivery_address:
        lines.append(f"🏠 Адрес: {order.delivery_address}")

    lines.append(f"💳 Оплата: {order.get_payment_method_display()}")
    lines.append("")

    # Товары
    lines.append("📦 Товары:")
    for item in order.items.all():
        lines.append(
            f"- {item.product_name} × {item.quantity} = {item.get_total_price()} ₽"
        )

    lines.extend([
        "",
        f"💰 Итого: {order.total_price} ₽",
    ])

    # Если хочешь, можно добавить ссылку в админку:
    admin_url = f"https://letsplayekb.shop/admin/main/order/{order.id}/change/"
    lines.append(f"🔗 Админка: {admin_url}")

    text = "\n".join(lines)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",  # если захочешь жирный текст и т.д.
    }

    try:
        resp = requests.post(url, data=data, timeout=5)
        if resp.status_code != 200:
            logger.warning("Telegram notify failed: %s", resp.text)
    except Exception as e:
        logger.exception("Error sending telegram notification about new order")
