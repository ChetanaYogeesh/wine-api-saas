import stripe
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.database import Base

stripe.api_key = None


def init_stripe(api_key: str):
    """Initialize Stripe with API key"""
    stripe.api_key = api_key


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True)
    stripe_price_id = Column(String(255), nullable=True)
    tier = Column(String(50), default="free")
    status = Column(String(50), default="inactive")
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="subscription")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_payment_method_id = Column(String(255), unique=True, nullable=False)
    brand = Column(String(50), nullable=True)
    last4 = Column(String(4), nullable=True)
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payment_methods")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_invoice_id = Column(String(255), unique=True, nullable=False)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="usd")
    status = Column(String(50), nullable=False)
    invoice_pdf = Column(String(500), nullable=True)
    invoice_url = Column(String(500), nullable=True)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="invoices")


class UsageAlert(Base):
    __tablename__ = "usage_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    threshold_percent = Column(Integer, nullable=False)
    last_sent_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="usage_alerts")


TIER_PRICES = {
    "free": {
        "price_id": None,
        "monthly_requests": 1000,
        "rate_limit": 60,
        "price": 0,
    },
    "pro": {
        "price_id": "price_pro_monthly",  # Replace with actual Stripe price ID
        "monthly_requests": 50000,
        "rate_limit": 300,
        "price": 29,
    },
    "enterprise": {
        "price_id": "price_enterprise_monthly",  # Replace with actual Stripe price ID
        "monthly_requests": 1000000,
        "rate_limit": 1000,
        "price": 99,
    },
}


def create_stripe_customer(email: str, name: str) -> stripe.Customer:
    """Create a Stripe customer"""
    return stripe.Customer.create(
        email=email,
        name=name,
    )


def create_stripe_subscription(
    customer_id: str,
    price_id: str,
) -> stripe.Subscription:
    """Create a Stripe subscription"""
    return stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        payment_behavior="default_incomplete",
        expand=["latest_invoice.payment_intent"],
    )


def cancel_stripe_subscription(subscription_id: str) -> stripe.Subscription:
    """Cancel a Stripe subscription at period end"""
    return stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=True,
    )


def reactivate_stripe_subscription(subscription_id: str) -> stripe.Subscription:
    """Reactivate a cancelled subscription"""
    return stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=False,
    )


def create_stripe_checkout_session(
    customer_id: str,
    price_id: str,
    success_url: str,
    cancel_url: str,
) -> stripe.checkout.Session:
    """Create a Stripe checkout session"""
    return stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
    )


def create_stripe_portal_session(
    customer_id: str,
    return_url: str,
) -> stripe.billing_portal.Session:
    """Create a Stripe customer portal session"""
    return stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )


def get_stripe_subscription(subscription_id: str) -> stripe.Subscription:
    """Get subscription details from Stripe"""
    return stripe.Subscription.retrieve(subscription_id)


def handle_stripe_webhook(
    payload: bytes,
    sig_header: str,
    webhook_secret: str,
) -> stripe.Event:
    """Verify and parse Stripe webhook"""
    return stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
