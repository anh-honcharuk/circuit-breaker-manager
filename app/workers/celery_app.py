from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "resilience_platform",
    broker=settings.redis_url,
    backend=settings.redis_url,
)