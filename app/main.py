import os
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
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
from app.models import User, Wine, APIKey, UsageLog, TIER_LIMITS
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
)

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
    return {"detail": "Rate limit exceeded. Please try again later."}


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
                    import time

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

    db_key = (
        db.query(APIKey).filter(APIKey.key == api_key, APIKey.is_active == True).first()
    )
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


@app.get("/wines/stats", response_model=WineStats)
@limiter.limit("60/minute")
async def wine_stats(
    request: Request,
    api_key: APIKey = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    from app.cache import stats_cache

    cached = stats_cache.get("stats")
    if cached:
        return WineStats(**cached)

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

    stats = {
        "total_wines": total,
        "avg_rating": round(avg_rating, 2),
        "top_region": top_region,
        "rating_distribution": distribution,
    }

    stats_cache.set("stats", stats)

    return WineStats(**stats)


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
    requests_today = len([l for l in logs if l.timestamp >= today_start])
    requests_this_month = len([l for l in logs if l.timestamp >= month_start])

    response_times = [l.response_time_ms for l in logs if l.response_time_ms]
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
