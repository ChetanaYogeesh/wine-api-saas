from datetime import datetime, timedelta
from app.models import UsageAlert, User, APIKey, UsageLog
from app.database import SessionLocal
from app.email import send_email


def check_usage_alerts():
    """Check usage and send alerts for users approaching limits"""
    db = SessionLocal()
    try:
        alerts = db.query(UsageAlert).filter(UsageAlert.is_active).all()

        for alert in alerts:
            if alert.last_sent_at:
                last_sent = (
                    alert.last_sent_at.replace(tzinfo=None)
                    if alert.last_sent_at.tzinfo
                    else alert.last_sent_at
                )
                if datetime.utcnow() - last_sent < timedelta(days=1):
                    continue

            user = db.query(User).filter(User.id == alert.user_id).first()
            if not user or not user.is_active:
                continue

            api_keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()
            if not api_keys:
                continue

            month_start = datetime.utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

            total_requests = 0
            for api_key in api_keys:
                count = (
                    db.query(UsageLog)
                    .filter(
                        UsageLog.api_key_id == api_key.id,
                        UsageLog.timestamp >= month_start,
                    )
                    .count()
                )
                total_requests += count

            tier_limit = api_keys[0].monthly_limit if api_keys else 1000
            usage_percent = (total_requests / tier_limit * 100) if tier_limit > 0 else 0

            if usage_percent >= alert.threshold_percent:
                send_usage_alert_email(user, total_requests, tier_limit, usage_percent)
                alert.last_sent_at = datetime.utcnow()
                db.commit()

    finally:
        db.close()


def send_usage_alert_email(user: User, usage: int, limit: int, percent: float):
    """Send usage alert email to user"""
    subject = f"⚠️ Wine API Usage Alert - {percent:.0f}% of monthly limit used"
    body = f"""
    Hi {user.full_name or "there"},
    
    This is a usage alert for your Wine API account.
    
    You've used {usage:,} out of your {limit:,} monthly API requests ({percent:.0f}%).
    
    {"Upgrade to Pro for 50,000 requests/month" if percent >= 80 else ""}
    
    View your usage dashboard: https://app.wineapi.com/dashboard
    
    Thanks,
    Wine API Team
    """

    try:
        send_email(user.email, subject, body)
    except Exception as e:
        print(f"Failed to send usage alert email: {e}")
