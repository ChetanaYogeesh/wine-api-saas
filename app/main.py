from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Query, HTTPException, Request, Depends
from fastapi.security import (
    APIKeyHeader,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from app.database import get_db, settings, engine, Base
from app.models import (
    User,
    Wine,
    APIKey,
    UsageLog,
    TIER_LIMITS,
    Webhook,
    WebhookDelivery,
    Team,
    TeamMember,
    WhiteLabelConfig,
)
from app.schemas import (
    Wine as WineSchema,
    WineListResponse,
    WineStats,
    UserCreate,
    UserResponse,
    Token,
    APIKeyCreate,
    APIKeyResponse,
    UsageStats,
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookDeliveryResponse,
    AnalyticsResponse,
    UsageByDay,
    UsageByEndpoint,
    UsageByStatus,
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamMemberResponse,
    TeamAddMember,
    TeamUpdateMember,
    WhiteLabelCreate,
    WhiteLabelUpdate,
    WhiteLabelResponse,
    SubscriptionResponse,
    PaymentMethodResponse,
    InvoiceResponse,
    UsageAlertCreate,
    UsageAlertResponse,
    CheckoutSessionResponse,
    PortalSessionResponse,
    PricingResponse,
    PricingTierResponse,
)
from app.payments import (
    Subscription,
    PaymentMethod,
    Invoice,
    UsageAlert,
    TIER_PRICES,
    create_stripe_customer,
    create_stripe_checkout_session,
    create_stripe_portal_session,
    init_stripe,
)
from app import models  # Import all models to register them with SQLAlchemy

pwd_context = None


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


app = FastAPI(title="Wine API", version="0.1.0")


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def check_monthly_limit(db_key: APIKey, db: Session) -> bool:
    """Check if user has exceeded their monthly limit"""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    request_count = (
        db.query(UsageLog)
        .filter(UsageLog.api_key_id == db_key.id, UsageLog.timestamp >= month_start)
        .count()
    )

    return request_count < db_key.monthly_limit


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
        headers={"Retry-After": "60"},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)


@app.middleware("http")
async def track_usage(request: Request, call_next):
    """Track API usage for each request"""
    start_time = datetime.utcnow()

    response = await call_next(request)

    # Only track API endpoints
    if (
        request.url.path.startswith("/wines")
        or request.url.path.startswith("/regions")
        or request.url.path.startswith("/varieties")
    ):
        # Get API key from header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            from app.database import SessionLocal

            db = SessionLocal()
            try:
                db_key = db.query(APIKey).filter(APIKey.key == api_key).first()
                if db_key:
                    response_time = int(
                        (datetime.utcnow() - start_time).total_seconds() * 1000
                    )

                    log = UsageLog(
                        api_key_id=db_key.id,
                        user_id=db_key.user_id,
                        endpoint=request.url.path,
                        method=request.method,
                        status_code=response.status_code,
                        response_time_ms=response_time,
                    )
                    db.add(log)
                    db.commit()
            finally:
                db.close()

    return response


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


async def verify_api_key(
    request: Request,
    api_key: str = Depends(security_header),
    db: Session = Depends(get_db),
):
    if not api_key:
        raise HTTPException(status_code=403, detail="API key required")

    db_key = db.query(APIKey).filter(APIKey.key == api_key, APIKey.is_active).first()
    if not db_key:
        raise HTTPException(status_code=403, detail="Invalid API key")

    if not check_monthly_limit(db_key, db):
        raise HTTPException(
            status_code=429,
            detail="Monthly API limit exceeded. Please upgrade your plan.",
        )

    return db_key


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Welcome to Wine API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api-keys", response_model=APIKeyResponse)
@limiter.limit("20/minute")
async def create_api_key(
    request: Request,
    api_key: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import secrets

    key = secrets.token_urlsafe(32)

    tier = api_key.tier
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])

    db_key = APIKey(
        key=key,
        name=api_key.name,
        user_id=current_user.id,
        tier=tier,
        rate_limit=limits["rate_limit"],
        monthly_limit=limits["monthly_limit"],
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key


@app.get("/api-keys", response_model=list[APIKeyResponse])
def list_api_keys(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return db.query(APIKey).filter(APIKey.user_id == current_user.id).all()


@app.get("/wines", response_model=WineListResponse)
@limiter.limit("60/minute")
async def list_wines(
    request: Request,
    api_key: APIKey = Depends(verify_api_key),
    region: Optional[str] = None,
    variety: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Wine)

    if region:
        query = query.filter(Wine.region.ilike(f"%{region}%"))
    if variety:
        query = query.filter(Wine.variety.ilike(f"%{variety}%"))
    if min_rating is not None:
        query = query.filter(Wine.rating >= min_rating)
    if max_rating is not None:
        query = query.filter(Wine.rating <= max_rating)

    total = query.count()
    wines = query.offset((page - 1) * limit).limit(limit).all()

    return WineListResponse(
        wines=[
            WineSchema(
                id=w.id,
                name=w.name,
                region=w.region,
                variety=w.variety,
                rating=w.rating,
                notes=w.notes,
            )
            for w in wines
        ],
        total=total,
        page=page,
        limit=limit,
    )


@app.get("/wines/stats", response_model=WineStats)
@limiter.limit("60/minute")
async def wine_stats(
    request: Request,
    api_key: APIKey = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    total = db.query(Wine).count()

    wines_with_rating = db.query(Wine).filter(Wine.rating.isnot(None)).all()
    avg_rating = (
        sum(w.rating for w in wines_with_rating) / len(wines_with_rating)
        if wines_with_rating
        else 0
    )

    regions = {}
    for w in wines_with_rating:
        if w.region:
            regions[w.region] = regions.get(w.region, 0) + 1
    top_region = max(regions, default="N/A")

    distribution = {"90-94": 0, "85-89": 0, "95+": 0, "0-85": 0}
    for w in wines_with_rating:
        if w.rating >= 95:
            distribution["95+"] += 1
        elif w.rating >= 90:
            distribution["90-94"] += 1
        elif w.rating >= 85:
            distribution["85-89"] += 1
        else:
            distribution["0-85"] += 1

    return WineStats(
        total_wines=total,
        avg_rating=round(avg_rating, 2),
        top_region=top_region,
        rating_distribution=distribution,
    )


@app.get("/wines/search", response_model=WineListResponse)
@limiter.limit("60/minute")
async def search_wines(
    request: Request,
    api_key: APIKey = Depends(verify_api_key),
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Wine).filter(
        (Wine.name.ilike(f"%{q}%")) | (Wine.notes.ilike(f"%{q}%"))
    )

    total = query.count()
    wines = query.offset((page - 1) * limit).limit(limit).all()

    return WineListResponse(
        wines=[
            WineSchema(
                id=w.id,
                name=w.name,
                region=w.region,
                variety=w.variety,
                rating=w.rating,
                notes=w.notes,
            )
            for w in wines
        ],
        total=total,
        page=page,
        limit=limit,
    )


@app.get("/wines/top-rated", response_model=WineListResponse)
@limiter.limit("60/minute")
async def top_rated_wines(
    request: Request,
    api_key: APIKey = Depends(verify_api_key),
    limit: int = Query(10, ge=1, le=100),
    region: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Wine).filter(Wine.rating.isnot(None)).order_by(Wine.rating.desc())

    if region:
        query = query.filter(Wine.region.ilike(f"%{region}%"))

    wines = query.limit(limit).all()

    return WineListResponse(
        wines=[
            WineSchema(
                id=w.id,
                name=w.name,
                region=w.region,
                variety=w.variety,
                rating=w.rating,
                notes=w.notes,
            )
            for w in wines
        ],
        total=len(wines),
        page=1,
        limit=limit,
    )


@app.get("/wines/{wine_id}", response_model=WineSchema)
@limiter.limit("60/minute")
async def get_wine(
    request: Request,
    wine_id: int,
    api_key: APIKey = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    wine = db.query(Wine).filter(Wine.id == wine_id).first()
    if not wine:
        raise HTTPException(status_code=404, detail="Wine not found")
    return wine


@app.get("/regions")
@limiter.limit("60/minute")
async def list_regions(
    request: Request,
    api_key: APIKey = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    from app.cache import regions_cache

    cached = regions_cache.get("list")
    if cached:
        return cached

    regions = db.query(Wine.region).distinct().filter(Wine.region.isnot(None)).all()
    result = {"regions": sorted([r[0] for r in regions if r[0]])}

    regions_cache.set("list", result)
    return result


@app.get("/regions/{region}/wines", response_model=WineListResponse)
@limiter.limit("60/minute")
async def get_wines_by_region(
    request: Request,
    region: str,
    api_key: APIKey = Depends(verify_api_key),
    variety: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Wine).filter(Wine.region.ilike(f"%{region}%"))

    if variety:
        query = query.filter(Wine.variety.ilike(f"%{variety}%"))
    if min_rating is not None:
        query = query.filter(Wine.rating >= min_rating)
    if max_rating is not None:
        query = query.filter(Wine.rating <= max_rating)

    total = query.count()
    wines = query.offset((page - 1) * limit).limit(limit).all()

    return WineListResponse(
        wines=[
            WineSchema(
                id=w.id,
                name=w.name,
                region=w.region,
                variety=w.variety,
                rating=w.rating,
                notes=w.notes,
            )
            for w in wines
        ],
        total=total,
        page=page,
        limit=limit,
    )


@app.get("/varieties")
@limiter.limit("60/minute")
async def list_varieties(
    request: Request,
    api_key: APIKey = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    from app.cache import varieties_cache

    cached = varieties_cache.get("list")
    if cached:
        return cached

    varieties = db.query(Wine.variety).distinct().filter(Wine.variety.isnot(None)).all()
    result = {"varieties": sorted([v[0] for v in varieties if v[0]])}

    varieties_cache.set("list", result)
    return result


@app.get("/usage", response_model=UsageStats)
@limiter.limit("30/minute")
async def get_usage_stats(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get usage statistics for the current user"""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    logs = db.query(UsageLog).filter(UsageLog.user_id == current_user.id).all()

    total_requests = len(logs)
    requests_today = len([log for log in logs if log.timestamp >= today_start])
    requests_this_month = len([log for log in logs if log.timestamp >= month_start])

    response_times = [log.response_time_ms for log in logs if log.response_time_ms]
    avg_response_time = (
        sum(response_times) / len(response_times) if response_times else 0
    )

    endpoint_counts = {}
    for log in logs:
        endpoint_counts[log.endpoint] = endpoint_counts.get(log.endpoint, 0) + 1
    top_endpoints = sorted(
        [{"endpoint": k, "count": v} for k, v in endpoint_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:5]

    status_counts = {}
    for log in logs:
        status_counts[str(log.status_code)] = (
            status_counts.get(str(log.status_code), 0) + 1
        )

    return UsageStats(
        total_requests=total_requests,
        requests_today=requests_today,
        requests_this_month=requests_this_month,
        avg_response_time_ms=round(avg_response_time, 2),
        top_endpoints=top_endpoints,
        requests_by_status=status_counts,
    )


@app.get("/tiers")
def list_tiers():
    """List available API tiers"""
    return {
        "tiers": [
            {
                "name": "free",
                "monthly_limit": 1000,
                "rate_limit": 60,
                "price": "$0/month",
            },
            {
                "name": "pro",
                "monthly_limit": 50000,
                "rate_limit": 300,
                "price": "$29/month",
            },
            {
                "name": "enterprise",
                "monthly_limit": 1000000,
                "rate_limit": 1000,
                "price": "$99/month",
            },
        ]
    }


@app.get("/v1/info")
def get_api_info():
    """Get API version information"""
    return {
        "name": "Wine API",
        "version": "1.0.0",
        "description": "Wine Data API",
        "documentation": "/docs",
        "tiers_endpoint": "/tiers",
    }


@app.get("/v1/health")
def health_check_v1():
    """Health check for v1"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/version")
def get_version():
    """Get current API version"""
    return {
        "version": "1.0.0",
        "release_date": "2026-03-16",
        "changelog": [
            "1.0.0 - Initial release with PostgreSQL, Redis caching, Celery tasks",
        ],
    }


def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


@app.post("/webhooks", response_model=WebhookResponse)
@limiter.limit("30/minute")
def create_webhook(
    webhook: WebhookCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Create a new webhook"""
    import secrets

    secret = secrets.token_hex(32)
    db_webhook = Webhook(
        user_id=current_user.id,
        url=webhook.url,
        events=",".join(webhook.events),
        secret=secret,
        is_active=True,
    )
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook


@app.get("/webhooks", response_model=list[WebhookResponse])
def list_webhooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """List all webhooks for current user"""
    webhooks = db.query(Webhook).filter(Webhook.user_id == current_user.id).all()
    return webhooks


@app.get("/webhooks/{webhook_id}", response_model=WebhookResponse)
def get_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Get a specific webhook"""
    webhook = (
        db.query(Webhook)
        .filter(Webhook.id == webhook_id, Webhook.user_id == current_user.id)
        .first()
    )
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook


@app.patch("/webhooks/{webhook_id}", response_model=WebhookResponse)
def update_webhook(
    webhook_id: int,
    webhook_update: WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Update a webhook"""
    webhook = (
        db.query(Webhook)
        .filter(Webhook.id == webhook_id, Webhook.user_id == current_user.id)
        .first()
    )
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    if webhook_update.url is not None:
        webhook.url = webhook_update.url
    if webhook_update.events is not None:
        webhook.events = ",".join(webhook_update.events)
    if webhook_update.is_active is not None:
        webhook.is_active = webhook_update.is_active

    db.commit()
    db.refresh(webhook)
    return webhook


@app.delete("/webhooks/{webhook_id}")
def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Delete a webhook"""
    webhook = (
        db.query(Webhook)
        .filter(Webhook.id == webhook_id, Webhook.user_id == current_user.id)
        .first()
    )
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    db.delete(webhook)
    db.commit()
    return {"detail": "Webhook deleted"}


@app.get(
    "/webhooks/{webhook_id}/deliveries", response_model=list[WebhookDeliveryResponse]
)
def list_webhook_deliveries(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """List delivery history for a webhook"""
    webhook = (
        db.query(Webhook)
        .filter(Webhook.id == webhook_id, Webhook.user_id == current_user.id)
        .first()
    )
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    deliveries = (
        db.query(WebhookDelivery)
        .filter(WebhookDelivery.webhook_id == webhook_id)
        .order_by(WebhookDelivery.created_at.desc())
        .limit(50)
        .all()
    )
    return deliveries


@app.post("/webhooks/events")
async def receive_webhook_event(
    event: str,
    payload: dict,
    db: Session = Depends(get_db),
):
    """Internal endpoint to trigger webhooks for an event"""
    webhooks = (
        db.query(Webhook)
        .filter(
            Webhook.is_active,
            Webhook.events.contains(event),
        )
        .all()
    )

    import httpx
    import json
    import hmac
    import hashlib

    for webhook in webhooks:
        payload_str = json.dumps(payload)
        signature = hmac.new(
            webhook.secret.encode(),
            payload_str.encode(),
            hashlib.sha256,
        ).hexdigest()

        delivery = WebhookDelivery(
            webhook_id=webhook.id,
            event=event,
            payload=payload_str,
            attempts=1,
        )
        db.add(delivery)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook.url,
                    content=payload_str,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": event,
                    },
                )
                delivery.status_code = response.status_code
                delivery.response_body = response.text[:1000]
                delivery.success = response.status_code < 400
        except Exception as e:
            delivery.status_code = 0
            delivery.response_body = str(e)[:1000]
            delivery.success = False

        db.commit()

    return {"delivered": len(webhooks)}


@app.get("/analytics", response_model=AnalyticsResponse)
@limiter.limit("30/minute")
def get_analytics(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Get detailed analytics for the current user"""
    from datetime import datetime, timezone, timedelta

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    logs = (
        db.query(UsageLog)
        .filter(
            UsageLog.user_id == current_user.id,
            UsageLog.timestamp >= cutoff,
        )
        .all()
    )

    total_requests = len(logs)
    avg_response_time = sum(log.response_time_ms or 0 for log in logs) / max(
        total_requests, 1
    )
    success_count = sum(1 for log in logs if log.status_code and log.status_code < 400)
    success_rate = (success_count / max(total_requests, 1)) * 100

    usage_by_day = {}
    for log in logs:
        date_str = log.timestamp.strftime("%Y-%m-%d")
        usage_by_day[date_str] = usage_by_day.get(date_str, 0) + 1

    usage_by_day_list = [
        UsageByDay(date=date, count=count)
        for date, count in sorted(usage_by_day.items())
    ]

    usage_by_endpoint = {}
    for log in logs:
        usage_by_endpoint[log.endpoint] = usage_by_endpoint.get(log.endpoint, 0) + 1

    usage_by_endpoint_list = [
        UsageByEndpoint(endpoint=ep, count=c)
        for ep, c in sorted(
            usage_by_endpoint.items(), key=lambda x: x[1], reverse=True
        )[:10]
    ]

    usage_by_status = {}
    for log in logs:
        if log.status_code:
            usage_by_status[log.status_code] = (
                usage_by_status.get(log.status_code, 0) + 1
            )

    usage_by_status_list = [
        UsageByStatus(status_code=sc, count=c)
        for sc, c in sorted(usage_by_status.items())
    ]

    return AnalyticsResponse(
        total_requests=total_requests,
        avg_response_time_ms=round(avg_response_time, 2),
        success_rate=round(success_rate, 2),
        usage_by_day=usage_by_day_list,
        usage_by_endpoint=usage_by_endpoint_list,
        usage_by_status=usage_by_status_list,
    )


@app.get("/analytics/export")
@limiter.limit("10/minute")
def export_analytics(
    request: Request,
    days: int = Query(30, ge=1, le=90),
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Export analytics data in JSON or CSV format"""
    from datetime import datetime, timezone, timedelta
    import csv
    import io

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    logs = (
        db.query(UsageLog)
        .filter(
            UsageLog.user_id == current_user.id,
            UsageLog.timestamp >= cutoff,
        )
        .order_by(UsageLog.timestamp.desc())
        .all()
    )

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            ["id", "endpoint", "method", "status_code", "response_time_ms", "timestamp"]
        )
        for log in logs:
            writer.writerow(
                [
                    log.id,
                    log.endpoint,
                    log.method,
                    log.status_code,
                    log.response_time_ms,
                    log.timestamp.isoformat(),
                ]
            )
        return {"data": output.getvalue(), "content_type": "text/csv"}
    else:
        return {
            "data": [
                {
                    "id": log.id,
                    "endpoint": log.endpoint,
                    "method": log.method,
                    "status_code": log.status_code,
                    "response_time_ms": log.response_time_ms,
                    "timestamp": log.timestamp.isoformat(),
                }
                for log in logs
            ],
            "content_type": "application/json",
        }


@app.post("/teams", response_model=TeamResponse)
@limiter.limit("20/minute")
def create_team(
    team: TeamCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Create a new team"""
    db_team = Team(name=team.name, owner_id=current_user.id)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@app.get("/teams", response_model=list[TeamResponse])
def list_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """List all teams the user belongs to"""
    owned_teams = db.query(Team).filter(Team.owner_id == current_user.id).all()
    memberships = (
        db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    )
    member_team_ids = [m.team_id for m in memberships]
    member_teams = (
        db.query(Team).filter(Team.id.in_(member_team_ids)).all()
        if member_team_ids
        else []
    )
    return owned_teams + member_teams


@app.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Get a specific team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    is_member = (
        team.owner_id == current_user.id
        or db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id)
        .first()
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    return team


@app.patch("/teams/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    team_update: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Update a team (owner only)"""
    team = (
        db.query(Team)
        .filter(Team.id == team_id, Team.owner_id == current_user.id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or not authorized")
    if team_update.name:
        team.name = team_update.name
    db.commit()
    db.refresh(team)
    return team


@app.delete("/teams/{team_id}")
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Delete a team (owner only)"""
    team = (
        db.query(Team)
        .filter(Team.id == team_id, Team.owner_id == current_user.id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or not authorized")
    db.query(TeamMember).filter(TeamMember.team_id == team_id).delete()
    db.delete(team)
    db.commit()
    return {"detail": "Team deleted"}


@app.post("/teams/{team_id}/members", response_model=TeamMemberResponse)
def add_team_member(
    team_id: int,
    member: TeamAddMember,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Add a member to a team (owner only)"""
    team = (
        db.query(Team)
        .filter(Team.id == team_id, Team.owner_id == current_user.id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or not authorized")
    user = db.query(User).filter(User.email == member.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.user_id == user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")
    db_member = TeamMember(team_id=team_id, user_id=user.id, role=member.role)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@app.get("/teams/{team_id}/members", response_model=list[TeamMemberResponse])
def list_team_members(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """List team members"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    is_member = (
        team.owner_id == current_user.id
        or db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id)
        .first()
    )
    if not is_member:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    result = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        if user:
            result.append(
                TeamMemberResponse(
                    id=m.id,
                    user_id=m.user_id,
                    email=user.email,
                    full_name=user.full_name,
                    role=m.role,
                    created_at=m.created_at,
                )
            )
    return result


@app.patch("/teams/{team_id}/members/{member_id}", response_model=TeamMemberResponse)
def update_team_member(
    team_id: int,
    member_id: int,
    member_update: TeamUpdateMember,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Update a team member's role (owner only)"""
    team = (
        db.query(Team)
        .filter(Team.id == team_id, Team.owner_id == current_user.id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or not authorized")
    member = (
        db.query(TeamMember)
        .filter(TeamMember.id == member_id, TeamMember.team_id == team_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    member.role = member_update.role
    db.commit()
    db.refresh(member)
    user = db.query(User).filter(User.id == member.user_id).first()
    return TeamMemberResponse(
        id=member.id,
        user_id=member.user_id,
        email=user.email,
        full_name=user.full_name,
        role=member.role,
        created_at=member.created_at,
    )


@app.delete("/teams/{team_id}/members/{member_id}")
def remove_team_member(
    team_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Remove a team member (owner only)"""
    team = (
        db.query(Team)
        .filter(Team.id == team_id, Team.owner_id == current_user.id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or not authorized")
    member = (
        db.query(TeamMember)
        .filter(TeamMember.id == member_id, TeamMember.team_id == team_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()
    return {"detail": "Member removed"}


@app.post("/white-label", response_model=WhiteLabelResponse)
@limiter.limit("10/minute")
def create_white_label_config(
    config: WhiteLabelCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Create white-label configuration"""
    existing = (
        db.query(WhiteLabelConfig)
        .filter(WhiteLabelConfig.user_id == current_user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="White-label config already exists")
    db_config = WhiteLabelConfig(
        user_id=current_user.id, **config.dict(exclude_unset=True)
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@app.get("/white-label", response_model=WhiteLabelResponse)
def get_white_label_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Get white-label configuration"""
    config = (
        db.query(WhiteLabelConfig)
        .filter(WhiteLabelConfig.user_id == current_user.id)
        .first()
    )
    if not config:
        raise HTTPException(status_code=404, detail="White-label config not found")
    return config


@app.patch("/white-label", response_model=WhiteLabelResponse)
def update_white_label_config(
    config_update: WhiteLabelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Update white-label configuration"""
    config = (
        db.query(WhiteLabelConfig)
        .filter(WhiteLabelConfig.user_id == current_user.id)
        .first()
    )
    if not config:
        raise HTTPException(status_code=404, detail="White-label config not found")
    for key, value in config_update.dict(exclude_unset=True).items():
        setattr(config, key, value)
    db.commit()
    db.refresh(config)
    return config


@app.delete("/white-label")
def delete_white_label_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Delete white-label configuration"""
    config = (
        db.query(WhiteLabelConfig)
        .filter(WhiteLabelConfig.user_id == current_user.id)
        .first()
    )
    if not config:
        raise HTTPException(status_code=404, detail="White-label config not found")
    db.delete(config)
    db.commit()
    return {"detail": "White-label config deleted"}


# ==================== Payment & Subscription Endpoints ====================


@app.get("/pricing", response_model=PricingResponse)
def get_pricing():
    """Get pricing information"""
    tiers = []
    for tier_name, tier_info in TIER_PRICES.items():
        tiers.append(
            PricingTierResponse(
                tier=tier_name,
                price=tier_info["price"],
                monthly_requests=tier_info["monthly_requests"],
                rate_limit=tier_info["rate_limit"],
                features=_get_tier_features(tier_name),
            )
        )
    return PricingResponse(tiers=tiers, current_tier="free")


def _get_tier_features(tier: str) -> list[str]:
    features = {
        "free": [
            "1,000 API requests/month",
            "60 requests/minute",
            "Basic support",
        ],
        "pro": [
            "50,000 API requests/month",
            "300 requests/minute",
            "Priority support",
            "Analytics dashboard",
        ],
        "enterprise": [
            "1,000,000 API requests/month",
            "1,000 requests/minute",
            "Dedicated support",
            "Custom rate limits",
            "Team management",
            "White-label",
        ],
    }
    return features.get(tier, [])


@app.post("/subscription/checkout", response_model=CheckoutSessionResponse)
def create_checkout_session(
    tier: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Create Stripe checkout session for subscription upgrade"""
    if tier not in TIER_PRICES:
        raise HTTPException(status_code=400, detail="Invalid tier")

    tier_info = TIER_PRICES[tier]
    if not tier_info["price_id"]:
        raise HTTPException(status_code=400, detail="Free tier cannot be purchased")

    init_stripe(settings.stripe_api_key)

    subscription = (
        db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    )

    if not subscription or not subscription.stripe_customer_id:
        customer = create_stripe_customer(
            current_user.email, current_user.full_name or ""
        )
        if not subscription:
            subscription = Subscription(user_id=current_user.id)
            db.add(subscription)
        subscription.stripe_customer_id = customer.id
        db.commit()

    base_url = settings.allowed_origins.split(",")[0].strip()
    session = create_stripe_checkout_session(
        customer_id=subscription.stripe_customer_id,
        price_id=tier_info["price_id"],
        success_url=f"{base_url}/dashboard?upgrade=success",
        cancel_url=f"{base_url}/dashboard?upgrade=cancelled",
    )

    return CheckoutSessionResponse(
        checkout_url=session.url,
        session_id=session.id,
    )


@app.post("/subscription/portal", response_model=PortalSessionResponse)
def create_portal_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Create Stripe customer portal session"""
    init_stripe(settings.stripe_api_key)

    subscription = (
        db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    )

    if not subscription or not subscription.stripe_customer_id:
        raise HTTPException(status_code=404, detail="No subscription found")

    base_url = settings.allowed_origins.split(",")[0].strip()
    portal_session = create_stripe_portal_session(
        customer_id=subscription.stripe_customer_id,
        return_url=f"{base_url}/dashboard",
    )

    return PortalSessionResponse(portal_url=portal_session.url)


@app.get("/subscription", response_model=SubscriptionResponse)
def get_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Get current subscription info"""
    subscription = (
        db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    )

    if not subscription:
        subscription = Subscription(
            user_id=current_user.id, tier="free", status="inactive"
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)

    return subscription


@app.post("/subscription/cancel")
def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Cancel subscription at period end"""
    init_stripe(settings.stripe_api_key)

    subscription = (
        db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    )

    if not subscription or not subscription.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription")

    from app.payments import cancel_stripe_subscription

    cancel_stripe_subscription(subscription.stripe_subscription_id)

    subscription.cancel_at_period_end = True
    db.commit()

    return {"detail": "Subscription will be cancelled at period end"}


# ==================== Usage Alerts Endpoints ====================


@app.get("/usage/alerts", response_model=list[UsageAlertResponse])
def list_usage_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """List usage alerts"""
    alerts = db.query(UsageAlert).filter(UsageAlert.user_id == current_user.id).all()
    return alerts


@app.post("/usage/alerts", response_model=UsageAlertResponse)
def create_usage_alert(
    alert: UsageAlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Create a usage alert"""
    existing_alert = (
        db.query(UsageAlert)
        .filter(
            UsageAlert.user_id == current_user.id,
            UsageAlert.threshold_percent == alert.threshold_percent,
        )
        .first()
    )
    if existing_alert:
        raise HTTPException(
            status_code=400, detail="Alert for this threshold already exists"
        )

    new_alert = UsageAlert(
        user_id=current_user.id, threshold_percent=alert.threshold_percent
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert


@app.delete("/usage/alerts/{alert_id}")
def delete_usage_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Delete a usage alert"""
    alert = (
        db.query(UsageAlert)
        .filter(UsageAlert.id == alert_id, UsageAlert.user_id == current_user.id)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alert)
    db.commit()
    return {"detail": "Alert deleted"}


# ==================== Invoice Endpoints ====================


@app.get("/invoices", response_model=list[InvoiceResponse])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """List user invoices"""
    invoices = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id)
        .order_by(Invoice.created_at.desc())
        .all()
    )
    return invoices


@app.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token),
):
    """Get invoice details"""
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.user_id == current_user.id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
