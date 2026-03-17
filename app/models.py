from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    api_keys = relationship("APIKey", back_populates="user")
    usage_logs = relationship("UsageLog", back_populates="user")
    webhooks = relationship("Webhook", back_populates="user")
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    payment_methods = relationship("PaymentMethod", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")
    usage_alerts = relationship("UsageAlert", back_populates="user")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members = relationship("TeamMember", back_populates="team")
    owner = relationship("User", foreign_keys=[owner_id])


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="members")
    user = relationship("User")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=60)
    monthly_limit = Column(Integer, default=10000)
    tier = Column(String(50), default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="api_keys")
    team = relationship("Team")


TIER_LIMITS = {
    "free": {"monthly_limit": 1000, "rate_limit": 60},
    "pro": {"monthly_limit": 50000, "rate_limit": 300},
    "enterprise": {"monthly_limit": 1000000, "rate_limit": 1000},
}


class Wine(Base):
    __tablename__ = "wines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    region = Column(String(255), index=True)
    variety = Column(String(255), index=True)
    rating = Column(Float)
    notes = Column(Text)
    country = Column(String(100))
    vintage = Column(Integer)
    price = Column(Float)
    image_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WinePriceHistory(Base):
    __tablename__ = "wine_price_history"

    id = Column(Integer, primary_key=True, index=True)
    wine_id = Column(Integer, ForeignKey("wines.id"), nullable=False)
    price = Column(Float, nullable=False)
    retailer = Column(String(255))
    url = Column(String(500))
    currency = Column(String(3), default="USD")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class WineRecommendation(Base):
    __tablename__ = "wine_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    wine_id = Column(Integer, ForeignKey("wines.id"), nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    wine = relationship("Wine")


class WinePreference(Base):
    __tablename__ = "wine_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    preferred_region = Column(String(255))
    preferred_variety = Column(String(255))
    min_rating = Column(Float)
    max_price = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id = Column(Integer, primary_key=True, index=True)
    wine_id = Column(Integer, ForeignKey("wines.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    condition = Column(String(50))
    description = Column(Text)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    wine = relationship("Wine")
    seller = relationship("User")


class MarketplaceTransaction(Base):
    __tablename__ = "marketplace_transactions"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("marketplace_listings.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    status = Column(String(20), default="pending")
    payment_status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    listing = relationship("MarketplaceListing")


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="usage_logs")


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    url = Column(String(500), nullable=False)
    events = Column(String(255))
    secret = Column(String(64))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="webhooks")
    deliveries = relationship("WebhookDelivery", back_populates="webhook")


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False)
    event = Column(String(100), nullable=False)
    payload = Column(Text)
    status_code = Column(Integer)
    response_body = Column(Text)
    success = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    webhook = relationship("Webhook", back_populates="deliveries")


class WhiteLabelConfig(Base):
    __tablename__ = "white_label_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    company_name = Column(String(255))
    logo_url = Column(String(500))
    primary_color = Column(String(7))
    secondary_color = Column(String(7))
    custom_domain = Column(String(255), unique=True, index=True)
    email_footer = Column(Text)
    is_active = Column(Boolean, default=True)
    ssl_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")
