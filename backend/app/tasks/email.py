"""Email-related background tasks."""

from celery import shared_task
from app.core.logging import get_logger

logger = get_logger(__name__)


@shared_task
def send_welcome_email(user_email: str, user_name: str) -> bool:
    """Send welcome email to new user."""
    logger.info(f"Sending welcome email to {user_email}")
    # TODO: Implement actual email sending logic
    return True


@shared_task
def send_password_reset_email(user_email: str, reset_token: str) -> bool:
    """Send password reset email."""
    logger.info(f"Sending password reset email to {user_email}")
    # TODO: Implement actual email sending logic
    return True
