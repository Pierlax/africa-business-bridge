"""
Celery Configuration Module for Africa Business Bridge

This module configures Celery for asynchronous task processing,
including long-running operations like PDF generation and AI matching.
"""

from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery app
celery_app = Celery(
    "africa_business_bridge",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Periodic tasks (scheduled)
    beat_schedule={
        "refresh-market-intelligence": {
            "task": "app.tasks.market_intelligence.refresh_market_news",
            "schedule": crontab(hour="*/6"),  # Every 6 hours
        },
        "cleanup-old-sessions": {
            "task": "app.tasks.maintenance.cleanup_old_sessions",
            "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
        },
        "generate-analytics-reports": {
            "task": "app.tasks.analytics.generate_daily_reports",
            "schedule": crontab(hour=1, minute=0),  # Daily at 1 AM
        },
    },
)

# Task routing configuration
celery_app.conf.task_routes = {
    "app.tasks.certificates.*": {"queue": "certificates"},
    "app.tasks.matching.*": {"queue": "matching"},
    "app.tasks.market_intelligence.*": {"queue": "market_intelligence"},
    "app.tasks.maintenance.*": {"queue": "maintenance"},
}

# Task rate limiting
celery_app.conf.task_default_rate_limit = "100/m"  # 100 tasks per minute by default

# Error handling
celery_app.conf.task_acks_late = True  # Acknowledge task after execution
celery_app.conf.task_reject_on_worker_lost = True  # Reject task if worker dies


@celery_app.task(bind=True, max_retries=3)
def debug_task(self):
    """Debug task for testing Celery setup."""
    try:
        print(f"Request: {self.request!r}")
        return "Celery is working!"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

