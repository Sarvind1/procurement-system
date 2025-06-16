"""Celery configuration for background tasks."""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "procurement_system",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.email",
        "app.tasks.notifications",
        "app.tasks.reports",
    ]
)

# Configure Celery
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Beat schedule for periodic tasks
    beat_schedule={
        # Example periodic tasks
        "cleanup-old-sessions": {
            "task": "app.tasks.maintenance.cleanup_sessions",
            "schedule": 3600.0,  # Every hour
        },
        "generate-daily-reports": {
            "task": "app.tasks.reports.generate_daily_report",
            "schedule": 86400.0,  # Every day
        },
    },
    
    # Routing
    task_routes={
        "app.tasks.email.*": {"queue": "email"},
        "app.tasks.reports.*": {"queue": "reports"},
        "app.tasks.notifications.*": {"queue": "notifications"},
    },
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
)

# Export the celery app
app = celery_app

if __name__ == "__main__":
    celery_app.start()
