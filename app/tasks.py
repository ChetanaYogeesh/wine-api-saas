from celery import Celery
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()

celery_app = Celery(
    "wineapi",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)


@celery_app.task(name="app.tasks.send_welcome_email")
def send_welcome_email(email: str, name: str):
    """Send welcome email to new users"""
    print(f"Sending welcome email to {email} ({name})")
    return {"status": "sent", "email": email}


@celery_app.task(name="app.tasks.send_api_key_created_email")
def send_api_key_created_email(email: str, key_name: str):
    """Send email when API key is created"""
    print(f"Sending API key creation email to {email} for key: {key_name}")
    return {"status": "sent", "email": email}


@celery_app.task(name="app.tasks.cleanup_old_logs")
def cleanup_old_logs(days: int = 90):
    """Clean up usage logs older than specified days"""
    print(f"Cleaning up logs older than {days} days")
    return {"status": "completed", "days": days}


@celery_app.task(name="app.tasks.generate_monthly_report")
def generate_monthly_report(user_id: int):
    """Generate monthly usage report for user"""
    print(f"Generating monthly report for user {user_id}")
    return {"status": "completed", "user_id": user_id}
