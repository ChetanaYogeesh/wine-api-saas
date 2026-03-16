from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@wineapi.com"
    from_name: str = "Wine API"

    class Config:
        env_file = ".env"


settings = Settings()


def send_email(to: str, subject: str, body: str) -> bool:
    """Send email (placeholder - implement with actual SMTP)"""
    if not settings.smtp_user:
        print(f"[EMAIL] To: {to}, Subject: {subject}")
        return True

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg["From"] = f"{settings.from_name} <{settings.from_email}>"
        msg["To"] = to
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_welcome_email(email: str, name: str) -> bool:
    """Send welcome email to new users"""
    subject = "Welcome to Wine API!"
    body = f"""
    <html>
    <body>
        <h1>Welcome to Wine API, {name}!</h1>
        <p>Thank you for signing up. You can now:</p>
        <ul>
            <li>Create API keys in your dashboard</li>
            <li>Access 32,780+ wines</li>
            <li>Use our powerful search API</li>
        </ul>
        <p>Get started: <a href="http://localhost:3000/dashboard">Dashboard</a></p>
    </body>
    </html>
    """
    return send_email(email, subject, body)


def send_api_key_email(email: str, key_name: str, api_key: str) -> bool:
    """Send email with new API key"""
    subject = "Your New Wine API Key"
    body = f"""
    <html>
    <body>
        <h1>New API Key Created</h1>
        <p>Your API key "{key_name}" has been created:</p>
        <pre style="background: #f4f4f4; padding: 10px; border-radius: 5px;">{api_key}</pre>
        <p>Keep this key safe - it won't be shown again!</p>
    </body>
    </html>
    """
    return send_email(email, subject, body)
