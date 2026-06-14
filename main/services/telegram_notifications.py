import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_order_notification(order):
    """Send a minimal order alert without customer personal data."""
    if not getattr(settings, "TELEGRAM_ORDER_NOTIFICATIONS_ENABLED", False):
        return

    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_id = getattr(settings, "TELEGRAM_ADMIN_CHAT_ID", "")
    if not token or not chat_id:
        logger.warning("Telegram notification is enabled, but credentials are not set")
        return

    lines = [
        f"НОВЫЙ ЗАКАЗ №{order.id}",
        "",
        f"Доставка: {order.get_delivery_method_display()}",
        "Товары:",
    ]
    for item in order.items.all():
        lines.append(f"- {item.product_name} × {item.quantity} = {item.get_total_price()} ₽")
    lines.extend([
        "",
        f"Итого: {order.total_price} ₽",
        f"Админка: https://letsplayekb.shop/admin/main/order/{order.id}/change/",
    ])

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": "\n".join(lines)},
            timeout=5,
        )
        if response.status_code != 200:
            logger.warning("Telegram notify failed with status %s", response.status_code)
    except requests.RequestException:
        logger.exception("Error sending Telegram order notification")
