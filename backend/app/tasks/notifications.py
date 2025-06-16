"""Notification-related background tasks."""

from celery import shared_task
from app.core.logging import get_logger

logger = get_logger(__name__)


@shared_task
def send_order_notification(order_id: str, user_id: str) -> bool:
    """Send order status notification."""
    logger.info(f"Sending order notification for order {order_id} to user {user_id}")
    # TODO: Implement notification logic
    return True


@shared_task
def send_low_stock_alert(product_id: str, current_stock: int) -> bool:
    """Send low stock alert notification."""
    logger.info(f"Sending low stock alert for product {product_id}, current stock: {current_stock}")
    # TODO: Implement notification logic
    return True
