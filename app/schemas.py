from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class WineBase(BaseModel):
    name: str
    region: Optional[str] = None
    variety: Optional[str] = None
    rating: Optional[float] = None
    notes: Optional[str] = None


class Wine(WineBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WineListResponse(BaseModel):
    wines: list[Wine]
    total: int
    page: int
    limit: int


class WineStats(BaseModel):
    total_wines: int
    avg_rating: float
    top_region: str
    rating_distribution: dict[str, int]


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class APIKeyBase(BaseModel):
    name: Optional[str] = None
    tier: str = "free"


TIER_CHOICES = ["free", "pro", "enterprise"]


class APIKeyCreate(APIKeyBase):
    pass


class APIKeyResponse(APIKeyBase):
    id: int
    key: str
    user_id: int
    is_active: bool
    rate_limit: int
    monthly_limit: int
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsageLogResponse(BaseModel):
    id: int
    api_key_id: int
    user_id: int
    endpoint: str
    method: str
    status_code: int
    response_time_ms: Optional[int]
    timestamp: datetime

    class Config:
        from_attributes = True


class UsageStats(BaseModel):
    total_requests: int
    requests_today: int
    requests_this_month: int
    avg_response_time_ms: float
    top_endpoints: list[dict]
    requests_by_status: dict[str, int]


WEBHOOK_EVENTS = [
    "wine.created",
    "wine.updated",
    "wine.deleted",
    "api_key.created",
    "api_key.deleted",
    "usage.alert",
]


class WebhookBase(BaseModel):
    url: str
    events: list[str]


class WebhookCreate(WebhookBase):
    pass


class WebhookUpdate(BaseModel):
    url: Optional[str] = None
    events: Optional[list[str]] = None
    is_active: Optional[bool] = None


class WebhookResponse(WebhookBase):
    id: int
    user_id: int
    secret: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookDeliveryBase(BaseModel):
    event: str
    payload: str


class WebhookDeliveryResponse(WebhookDeliveryBase):
    id: int
    webhook_id: int
    status_code: Optional[int]
    response_body: Optional[str]
    success: bool
    attempts: int
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsBase(BaseModel):
    pass


class UsageByDay(BaseModel):
    date: str
    count: int


class UsageByEndpoint(BaseModel):
    endpoint: str
    count: int


class UsageByStatus(BaseModel):
    status_code: int
    count: int


class AnalyticsResponse(BaseModel):
    total_requests: int
    avg_response_time_ms: float
    success_rate: float
    usage_by_day: list[UsageByDay]
    usage_by_endpoint: list[UsageByEndpoint]
    usage_by_status: list[UsageByStatus]


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None


class TeamMemberResponse(BaseModel):
    id: int
    user_id: int
    email: str
    full_name: Optional[str]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class TeamResponse(TeamBase):
    id: int
    owner_id: int
    created_at: datetime
    members: list[TeamMemberResponse] = []

    class Config:
        from_attributes = True


class TeamAddMember(BaseModel):
    email: str
    role: str = "member"


class TeamUpdateMember(BaseModel):
    role: str


class WhiteLabelBase(BaseModel):
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    custom_domain: Optional[str] = None
    email_footer: Optional[str] = None


class WhiteLabelCreate(WhiteLabelBase):
    pass


class WhiteLabelUpdate(BaseModel):
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    custom_domain: Optional[str] = None
    email_footer: Optional[str] = None


class WhiteLabelResponse(WhiteLabelBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Payment Schemas
class SubscriptionBase(BaseModel):
    tier: str = "free"


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    stripe_customer_id: Optional[str]
    stripe_subscription_id: Optional[str]
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool

    class Config:
        from_attributes = True


class PaymentMethodBase(BaseModel):
    is_default: bool = False


class PaymentMethodResponse(PaymentMethodBase):
    id: int
    user_id: int
    stripe_payment_method_id: str
    brand: Optional[str]
    last4: Optional[str]
    exp_month: Optional[int]
    exp_year: Optional[int]

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: int
    user_id: int
    stripe_invoice_id: str
    amount: float
    currency: str
    status: str
    invoice_pdf: Optional[str]
    invoice_url: Optional[str]
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class UsageAlertBase(BaseModel):
    threshold_percent: int = 80


class UsageAlertCreate(UsageAlertBase):
    pass


class UsageAlertResponse(UsageAlertBase):
    id: int
    user_id: int
    last_sent_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


class PortalSessionResponse(BaseModel):
    portal_url: str


class PricingTierResponse(BaseModel):
    tier: str
    price: float
    monthly_requests: int
    rate_limit: int
    features: list[str]


class PricingResponse(BaseModel):
    tiers: list[PricingTierResponse]
    current_tier: str
