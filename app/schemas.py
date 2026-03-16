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
