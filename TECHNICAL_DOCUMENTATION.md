# Wine API SaaS - Technical Documentation

**Version:** 1.0  
**Date:** March 16, 2026

---

# Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Technology Stack](#2-technology-stack)
3. [Database Design](#3-database-design)
4. [API Design](#4-api-design)
5. [Authentication & Security](#5-authentication--security)
6. [Scalability Principles](#6-scalability-principles)
7. [Distributed Systems Theory](#7-distributed-systems-theory)
8. [Performance Optimization](#8-performance-optimization)
9. [Monitoring & Observability](#9-monitoring--observability)
10. [Disaster Recovery](#10-disaster-recovery)
11. [Future Enhancements](#11-future-enhancements)

---

# 1. System Architecture

## 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Web App   │  │ Mobile App  │  │  IoT Devic  │  │  Third-Party   │  │
│  │  (Next.js)  │  │   (React)   │  │   (Python)  │  │    (API)       │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            LOAD BALANCER                                    │
│                         (Cloud Provider / NGINX)                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │  API      │   │  API      │   │  API      │
            │  Instance │   │  Instance │   │  Instance │
            │   #1      │   │   #2      │   │   #3      │
            └───────────┘   └───────────┘   └───────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SERVICES LAYER                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   FastAPI   │  │   Redis    │  │   Celery    │  │    Webhooks    │  │
│  │   (Python)  │  │   Cache    │  │   Workers   │  │    Service     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │ PostgreSQL│   │   Redis  │   │  Object   │
            │  Primary  │   │   (Pub/   │   │  Storage  │
            │           │   │    Sub)   │   │   (S3)    │
            └───────────┘   └───────────┘   └───────────┘
```

## 1.2 Component Overview

### Client Layer
- **Web Application**: Next.js frontend running on Vercel or similar
- **Mobile Applications**: React Native or native iOS/Android
- **IoT Devices**: Python clients consuming REST API
- **Third-party APIs**: External services integrating via API keys

### Load Balancing Layer
- Distributes incoming traffic across multiple API instances
- Provides SSL/TLS termination
- Implements rate limiting at the edge
- Health checking for instance monitoring

### Application Layer
- **FastAPI Application**: Handles HTTP requests, business logic
- **Redis Cache**: Caches frequently accessed data
- **Celery Workers**: Async task processing
- **Webhook Service**: Event-driven notifications

### Data Layer
- **PostgreSQL**: Primary data store
- **Redis**: Caching, session storage, pub/sub
- **Object Storage**: File storage (images, exports)

---

# 2. Technology Stack

## 2.1 Backend Technologies

### FastAPI (Python 3.12+)
```
Why FastAPI?
├── ASGI-based - Native async support
├── Automatic OpenAPI documentation
├── Pydantic for data validation
├── Type hints support
├── High performance (comparable to Node/Go)
└── Easy dependency injection
```

**Key Features Used:**
- Path operations with async/await
- Dependency injection for database sessions
- Middleware for cross-cutting concerns
- Exception handlers
- Background tasks

### SQLAlchemy 2.0
```
Why SQLAlchemy?
├── ORM with native SQL support
├── Async support (SQLAlchemy 2.0)
├── Connection pooling
├── Migration support (Alembic)
├── Type-safe queries
└── Multiple database support
```

### Pydantic 2.0
```
Why Pydantic?
├── Data validation
├── JSON serialization
├── Type coercion
├── Schema generation
├── Settings management
└── Performance (Rust-based)
```

## 2.2 Frontend Technologies

### Next.js 16
```
Architecture:
├── App Router (React Server Components)
├── Server-Side Rendering (SSR)
├── Static Site Generation (SSG)
├── API Routes
├── Image Optimization
└── Edge Runtime support
```

### React 18
- Concurrent rendering
- Automatic batching
- Suspense for data fetching

### Tailwind CSS
- Utility-first CSS framework
- Responsive design
- Dark mode support

## 2.3 Database Technologies

### PostgreSQL 16
```
Why PostgreSQL?
├── ACID compliance
├── Rich data types (JSON, Arrays)
├── Full-text search
├── Window functions
├── Materialized views
├── Replication support
├── Geographic data (PostGIS)
└── Extensibility
```

### Redis 7
```
Why Redis?
├── Sub-millisecond latency
├── Multiple data structures
├── Pub/Sub messaging
├── Lua scripting
├── Cluster mode
├── Persistence options
├── Lua transactions
└── Stream support
```

## 2.4 Infrastructure

### Docker & Containerization
```
Container Benefits:
├── Consistent environments
├── Resource isolation
├── Easy scaling
├── Fast deployment
├── Immutable infrastructure
└── Local development parity
```

### GitHub Actions (CI/CD)
```
Pipeline Stages:
├── Linting (ruff, black)
├── Testing (pytest)
├── Security scanning
├── Build (Docker)
├── Push to registry
├── Deploy to staging
├── Deploy to production
└── Smoke testing
```

---

# 3. Database Design

## 3.1 Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│      User       │       │     Team        │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │◄──────│ id (PK)         │
│ email           │       │ name            │
│ hashed_password │       │ owner_id (FK)   │
│ full_name       │       │ created_at      │
│ created_at      │       └────────┬────────┘
│ is_active       │                │
└────────┬────────┘                │
         │                         │
         │ 1:N                    │ 1:N
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│    APIKey      │       │   TeamMember    │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ user_id (FK)    │       │ team_id (FK)    │
│ team_id (FK)    │       │ user_id (FK)    │
│ key             │       │ role            │
│ name            │       │ joined_at       │
│ tier            │       └─────────────────┘
│ rate_limit      │
│ monthly_limit   │
│ is_active       │
│ created_at      │
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│      Wine      │       │   UsageLog      │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ name            │       │ api_key_id (FK) │
│ region          │       │ endpoint        │
│ variety         │       │ method          │
│ rating          │       │ status_code     │
│ vintage         │       │ response_time   │
│ price           │       │ timestamp       │
│ notes           │       │ user_id (FK)    │
│ created_at      │       └─────────────────┘
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│    Webhook     │       │WebhookDelivery │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ user_id (FK)    │◄──────│ webhook_id (FK) │
│ url             │       │ event           │
│ events          │       │ payload         │
│ secret          │       │ status          │
│ is_active       │       │ response_code   │
│ created_at      │       │ delivered_at    │
└─────────────────┘       └─────────────────┘
```

## 3.2 Indexing Strategy

```sql
-- Composite index for common queries
CREATE INDEX idx_wines_region_variety_rating 
ON wines(region, variety, rating DESC);

-- Partial index for active records
CREATE INDEX idx_api_keys_active 
ON api_keys(user_id) 
WHERE is_active = true;

-- Covering index for usage analytics
CREATE INDEX idx_usage_log_cover 
ON usage_logs(api_key_id, timestamp DESC) 
INCLUDE (endpoint, status_code);

-- Full-text search index
CREATE INDEX idx_wines_search 
ON wines 
USING GIN(to_tsvector('english', name || ' ' || region || ' ' || variety));
```

## 3.3 Query Optimization

### N+1 Problem Prevention
```python
# ❌ Bad: N+1 query
wines = db.query(Wine).all()
for wine in wines:
    print(wine.user.email)  # Each iteration = 1 query

# ✅ Good: Eager loading
wines = db.query(Wine).options(joinedload(Wine.user)).all()
```

### Pagination with Cursor
```python
# ❌ Bad: Offset pagination
wines = db.query(Wine).offset(10000).limit(10).all()

# ✅ Good: Cursor-based pagination
wines = db.query(Wine).filter(
    Wine.id > cursor
).order_by(Wine.id).limit(10).all()
```

---

# 4. API Design

## 4.1 RESTful Principles

### Resource-Oriented URLs
```
/wines              # Collection
/wines/123         # Single resource
/wines/search       # Action
/wines/stats       # Computed resource

/regions            # Collection
/regions/napa/wines # Nested resource
```

### HTTP Methods
| Method | Usage | Idempotent |
|--------|-------|------------|
| GET | Read | Yes |
| POST | Create | No |
| PUT | Replace | Yes |
| PATCH | Update | No |
| DELETE | Remove | Yes |

### Response Codes
```
2xx Success
├── 200 OK
├── 201 Created
├── 204 No Content

4xx Client Errors
├── 400 Bad Request
├── 401 Unauthorized
├── 403 Forbidden
├── 404 Not Found
├── 422 Validation Error
├── 429 Rate Limited

5xx Server Errors
├── 500 Internal Error
├── 503 Unavailable
```

## 4.2 API Versioning

```
Strategy: URL Path Versioning

/v1/wines
/v1/wines/123
/v2/wines (future)
```

Benefits:
- Clear contract
- Easy to deprecate
- Client control over version
- No header management

## 4.3 Rate Limiting Implementation

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/wines")
@limiter.limit("60/minute")
async def list_wines(request: Request):
    # Implementation
```

### Rate Limit Response Headers
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
Retry-After: 60
```

---

# 5. Authentication & Security

## 5.1 JWT Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │     │   API    │     │  Token  │     │   User  │
│          │     │          │     │ Issuer  │     │  Store   │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │               │               │               │
     │ 1. Login     │               │               │
     │─────────────►│               │               │
     │               │               │               │
     │ 2. Validate  │               │               │
     │──────────────┼──────────────►│               │
     │               │               │               │
     │ 3. User Data │◄──────────────┼──────────────┘
     │               │               │
     │               │               │
     │ 4. JWT Token │               │
     │◄─────────────│               │
     │               │               │
     │ 5. API Req   │               │
     │ (with JWT)   │               │
     │─────────────►│               │
     │               │               │
     │ 6. Verify    │               │
     │──────────────┼──────────────►│
     │               │               │
     │ 7. Response  │               │
     │◄─────────────│               │
```

## 5.2 API Key System

```python
# API Key Generation
def generate_api_key():
    import secrets
    return f"wine_{secrets.token_urlsafe(32)}"

# HMAC Signature for Webhooks
import hmac
import hashlib

def generate_signature(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
```

## 5.3 Security Headers

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

---

# 6. Scalability Principles

## 6.1 Horizontal vs Vertical Scaling

### Vertical Scaling (Scale Up)
```
Pros:
├── Simpler architecture
├── No code changes needed
├── Lower latency (shared memory)
└── Easier debugging

Cons:
├── Hardware limits
├── Single point of failure
├── Cost grows non-linearly
└── Downtime for upgrades
```

### Horizontal Scaling (Scale Out)
```
Pros:
├── Unlimited scale
├── Fault tolerance
├── Cost-effective (commodity hardware)
├── High availability
└── Independent scaling

Cons:
├── Complexity increases
├── Data consistency challenges
├── Network latency
└── Distributed debugging
```

## 6.2 The Scalability Pyramid

```
                    ┌─────────────┐
                    │   CDN &     │
                    │   Edge      │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Load       │
                    │  Balancer   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │  API    │  │  API    │  │  API    │
        │ Server  │  │ Server  │  │ Server  │
        └────┬────┘  └────┬────┘  └────┬────┘
             │            │            │
             └────────────┼────────────┘
                          ▼
              ┌───────────────────────┐
              │   Cache Layer        │
              │      (Redis)         │
              └───────────┬───────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │Primary DB│    │  Read    │    │  Queue   │
   │ (Write)  │    │ Replicas │    │(Celery)  │
   └──────────┘    └──────────┘    └──────────┘
```

## 6.3 Caching Strategies

### Cache-Aside Pattern
```python
def get_wine(wine_id: int):
    # 1. Check cache
    cache_key = f"wine:{wine_id}"
    wine = redis.get(cache_key)
    
    if wine:
        return json.loads(wine)
    
    # 2. Fetch from database
    wine = db.query(Wine).get(wine_id)
    
    # 3. Store in cache
    redis.setex(cache_key, 300, json.dumps(wine))
    
    return wine
```

### Write-Through Pattern
```python
def create_wine(data: WineCreate):
    # 1. Write to database
    wine = Wine(**data.dict())
    db.add(wine)
    db.commit()
    
    # 2. Update cache immediately
    redis.setex(f"wine:{wine.id}", 300, json.dumps(wine))
    
    return wine
```

### Cache Invalidation
```python
def update_wine(wine_id: int, data: WineUpdate):
    # 1. Update database
    wine = db.query(Wine).get(wine_id)
    for key, value in data.dict().items():
        setattr(wine, key, value)
    db.commit()
    
    # 2. Invalidate cache
    redis.delete(f"wine:{wine_id}")
    
    # 3. Optionally: Update with new data
    redis.setex(f"wine:{wine_id}", 300, json.dumps(wine))
```

## 6.4 Database Replication

### Primary-Replica Architecture
```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Primary    │       │   Replica  │       │   Replica  │
│  PostgreSQL │──────►│   #1       │──────►│   #2       │
│  (Writer)   │       │   (Reader) │       │   (Reader) │
└─────────────┘       └─────────────┘       └─────────────┘
      │                                        │
      │ WAL Streaming                          │
      ▼                                        ▼
┌─────────────┐                          ┌─────────────┐
│   pgpool   │                          │   HAProxy   │
│ (Pool/Rep) │                          │  (LB for    │
└─────────────┘                          │   Reads)   │
                                          └─────────────┘
```

### Read/Write Splitting
```python
# Configure two session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=primary_db)
ReadSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=replica_db)

def get_db():
    # Write operations
    if request.method in ['POST', 'PUT', 'DELETE']:
        return SessionLocal()
    # Read operations
    return ReadSessionLocal()
```

## 6.5 Queue-Based Async Processing

### Celery Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────►│   Redis    │────►│   Celery   │
│   (Producer)│     │   (Broker) │     │  (Worker)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │   Task      │
                                          │  Processing │
                                          └─────────────┘
```

### Example Tasks
```python
@celery.task
def process_wine_import(file_path: str):
    """Import wines from CSV file"""
    wines = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            wines.append(Wine(**row))
    
    # Batch insert
    db.bulk_insert_mappings(Wine, wines)
    db.commit()
    
    # Invalidate cache
    redis.delete_pattern("wines:*")
    
    return {"imported": len(wines)}

@celery.task
def deliver_webhook(webhook_id: int, event: str, payload: dict):
    """Deliver webhook asynchronously"""
    webhook = db.query(Webhook).get(webhook_id)
    
    response = requests.post(
        webhook.url,
        json={"event": event, "data": payload},
        headers={
            "X-Webhook-Signature": generate_signature(payload, webhook.secret)
        }
    )
    
    # Log delivery
    delivery = WebhookDelivery(
        webhook_id=webhook_id,
        event=event,
        payload=json.dumps(payload),
        status_code=response.status_code,
        delivered_at=datetime.utcnow()
    )
    db.add(delivery)
    db.commit()
```

---

# 7. Distributed Systems Theory

## 7.1 CAP Theorem

```
                Consistency
                    │
                    │
        ┌───────────┼───────────┐
        │                       │
        │    CA                 │    CP
        │ (Not Available)       │ (Not Consistent)
        │                       │
        ▼                       ▼
   ┌─────────┐            ┌─────────┐
   │Traditional│           │  Redis  │
   │  DBs    │            │ Cluster │
   └─────────┘            └─────────┘
        ▲                       ▲
        │                       │
        │                       │
        └───────────┬───────────┘
                    │
                    │
              Availability
```

**Our Choice: AP with Eventual Consistency**

- **Availability**: System always responds (even with stale data)
- **Partition Tolerance**: System works across network failures
- **Eventual Consistency**: Data propagates asynchronously

## 7.2 ACID vs BASE

### ACID (Traditional Databases)
```
Atomicity:  All or nothing
Consistency: Valid state to valid state
Isolation:   Concurrent = Sequential
Durability:  Written to disk
```

### BASE (Distributed Systems)
```
Basically Available:  System guarantees availability
Soft State:          State may change over time
Eventually Consistent: System will become consistent
```

## 7.3 Consensus in Distributed Systems

### Raft Consensus Algorithm
```
Terms (Epochs):
┌──────┐  ┌──────┐  ┌──────┐
│ Term │  │ Term │  │ Term │
│  1   │  │  2   │  │  3   │
└──────┘  └──────┘  └──────┘

States:
- Leader (writes)
- Follower (replicates)
- Candidate (election)

Election:
1. Follower timeout
2. Increment term
3. Request votes
4. Majority wins
```

**PostgreSQL uses Raft** for replication consensus.

## 7.4 Eventual Consistency Patterns

### Event Sourcing
```python
# Instead of storing state, store events

class WineCreatedEvent:
    wine_id: int
    name: str
    region: str
    timestamp: datetime

class WineUpdatedEvent:
    wine_id: int
    field: str
    old_value: Any
    new_value: Any
    timestamp: datetime

# Current state = Apply all events
def get_wine_state(wine_id: int) -> Wine:
    events = db.query(Event).filter(
        Event.aggregate_id == wine_id
    ).order_by(Event.timestamp)
    
    wine = Wine()
    for event in events:
        wine.apply(event)
    return wine
```

### CQRS (Command Query Responsibility Segregation)
```
Commands (Write)                    Queries (Read)
┌──────────────┐                   ┌──────────────┐
│   /wines     │                   │   /wines     │
│   (POST)     │                   │   (GET)      │
└──────┬───────┘                   └──────┬───────┘
       │                                  │
       ▼                                  ▼
┌──────────────┐                   ┌──────────────┐
│   Primary    │                   │   Read       │
│   Database   │───Event Bus──────▶│   Models     │
└──────────────┘                   │   (Cached)   │
                                   └──────────────┘
```

## 7.5 Distributed Tracing

```
Trace: Entire request journey
┌─────────────────────────────────────────────────────────────┐
│ Trace: api-wine-123                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────┐                                            │
│ │   Request   │                                            │
│ │   Received  │                                            │
│ └──────┬──────┘                                            │
│        │                                                    │
│        ▼                                                    │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│ │  Auth       │  │  Rate       │  │  Database   │          │
│ │  Middleware │─▶│  Limiter    │─▶│  Query      │          │
│ └─────────────┘  └─────────────┘  └─────────────┘          │
│        │                 │                 │                │
│        │                 │                 │                │
│     Span A            Span B            Span C              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# 8. Performance Optimization

## 8.1 Profiling Strategy

```python
# Application Performance Monitoring
import time
import logging

logger = logging.getLogger(__name__)

def profile(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        
        logger.info(
            f"{func.__name__} took {duration*1000:.2f}ms"
        )
        return result
    return wrapper

@profile
def expensive_operation():
    # Implementation
    pass
```

## 8.2 Database Query Optimization

### EXPLAIN Analysis
```sql
-- Analyze query performance
EXPLAIN ANALYZE 
SELECT w.*, u.email 
FROM wines w 
JOIN users u ON w.created_by = u.id 
WHERE w.region = 'Napa Valley' 
AND w.rating > 90
ORDER BY w.rating DESC
LIMIT 10;
```

### Connection Pooling
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # Open connections
    max_overflow=10,        # Overflow connections
    pool_pre_ping=True,     # Test connection
    pool_recycle=3600       # Recycle after 1 hour
)
```

## 8.3 Response Compression

```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Compression Ratio Example
```
Uncompressed:  100 KB
Gzip:          15 KB   (85% reduction)
Brotli:        12 KB   (88% reduction)
```

## 8.4 Async I/O Benefits

```python
# ❌ Blocking (sync)
def get_wines():
    wines = db.query(Wine).all()  # Blocks thread
    return wines

# ✅ Non-blocking (async)
async def get_wines():
    wines = await db.execute(select(Wine))  # Releases thread
    return wines
```

---

# 9. Monitoring & Observability

## 9.1 The Three Pillars

```
┌────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY                                │
│                                                                │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│   │  Logs    │    │ Metrics  │    │ Traces   │               │
│   ├──────────┤    ├──────────┤    ├──────────┤               │
│   │  "What   │    │  "How   │    │  "Where" │               │
│   │ happened?"│    │ much?"   │    │  now?"   │               │
│   └──────────┘    └──────────┘    └──────────┘               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Logs
- Structured JSON logging
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Correlation IDs for request tracing

### Metrics
- Request rate
- Error rate
- Response latency
- Resource utilization

### Traces
- Distributed request tracing
- Service dependencies
- Performance bottlenecks

## 9.2 Health Check Endpoints

```python
@app.get("/health")
async def health_check():
    checks = {
        "status": "healthy",
        "database": await check_database(),
        "redis": await check_redis(),
    }
    
    if not all(checks.values()):
        raise HTTPException(status_code=503)
    
    return checks

@app.get("/health/ready")
async def readiness_check():
    """Check if service can handle requests"""
    return {"ready": True}

@app.get("/health/live")
async def liveness_check():
    """Check if service is running"""
    return {"alive": True}
```

## 9.3 Alerting Rules

```yaml
# Prometheus alerting rules
groups:
  - name: wine-api
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
```

---

# 10. Disaster Recovery

## 10.1 Backup Strategy

```python
# Automated backup script
import subprocess
from datetime import datetime

def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"wineapi_backup_{timestamp}.sql"
    
    subprocess.run([
        "pg_dump",
        "-Fc",  # Custom format
        "-f", filename,
        "wineapi"
    ])
    
    # Upload to S3
    subprocess.run([
        "aws", "s3", "cp",
        filename,
        f"s3://backups.wineapi.com/{filename}"
    ])
```

### Backup Schedule
| Type | Frequency | Retention |
|------|-----------|------------|
| Full | Daily | 30 days |
| Incremental | Hourly | 7 days |
| WAL | Continuous | 7 days |
| Snapshots | Weekly | 90 days |

## 10.2 Recovery Procedures

```
RTO (Recovery Time Objective): 1 hour
RPO (Recovery Point Objective): 5 minutes
```

### Recovery Steps
1. Launch new database instance
2. Restore from latest snapshot
3. Apply WAL logs (point-in-time)
4. Verify data integrity
5. Update DNS/connection strings
6. Verify application health

## 10.3 Chaos Engineering

```yaml
# LitmusChaos experiment
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: pod-kill-chaos
spec:
  appinfo:
    appns: wine-api
    applabel: "app=wine-api"
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: '30'
            - name: CHAOS_INTERVAL
              value: '10'
```

---

# 11. Future Enhancements

## 11.1 GraphQL API

```graphql
type Wine {
  id: ID!
  name: String!
  region: Region!
  variety: Variety!
  rating: Float!
  wines(limit: Int): [Wine!]!
}

type Query {
  wines(
    region: String,
    variety: String,
    minRating: Float,
    first: Int,
    after: String
  ): WineConnection!
}
```

## 11.2 Real-time Subscriptions

```python
from fastapi import WebSocket

@app.websocket("/ws/wines")
async def websocket_wines(websocket: WebSocket):
    await websocket.accept()
    
    # Subscribe to wine updates
    pubsub = redis.pubsub()
    await pubsub.subscribe("wine-updates")
    
    async for message in pubsub.listen():
        await websocket.send_json(message)
```

## 11.3 Multi-Region Deployment

```
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│   US-East       │   │   EU-West       │   │   Asia-Pacific  │
│                  │   │                  │   │                  │
│  ┌────────────┐  │   │  ┌────────────┐  │   │  ┌────────────┐  │
│  │  Primary   │  │   │  │  Replica   │  │   │  │  Replica   │  │
│  │  Database  │  │   │  │            │  │   │  │            │  │
│  └────────────┘  │   │  └────────────┘  │   │  └────────────┘  │
│        │         │   │        │         │   │        │         │
│        └─────────┼───┴────────┴─────────┼───┴────────┘         │
│                  │                      │                      │
└──────────────────┴──────────────────────┴──────────────────────┘
                            │
                    ┌───────┴───────┐
                    │  Global DNS  │
                    │ (Route 53)   │
                    └───────────────┘
```

---

# Appendix: Key Formulas

## Little's Law
```
L = λ × W

L = Average number of items in system
λ = Average arrival rate
W = Average time in system

Example:
- 100 requests/second
- 0.5 seconds average response time
- L = 100 × 0.5 = 50 concurrent requests
```

## Amdahl's Law
```
S(n) = 1 / (P + (1-P)/n)

S = Speedup
P = Parallel portion
n = Number of processors

Example:
- 90% parallel, 10% serial
- 4 cores: S = 1 / (0.1 + 0.9/4) = 3.3x speedup
```

## Queueing Theory
```
 Utilization (ρ) = λ / μ
   - ρ < 1: Stable
   - ρ → 1: Congestion

 Response Time (W) = Wq + 1/μ
   - Wq = Average wait in queue
```

---

**Document Version:** 1.0  
**Last Updated:** March 16, 2026  
**Author:** Wine API SaaS Development Team
