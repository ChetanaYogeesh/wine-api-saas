# Wine API SaaS - Development Guide

## Development Phases

All 6 phases are complete! This guide covers how the project was built and how to continue development.

---

## Phase 1: Foundation ✅

**Goal:** Core API with database and authentication

### Implementation
1. **Database** (`app/database.py`)
   - SQLAlchemy setup with PostgreSQL
   - Session management

2. **Models** (`app/models.py`)
   - User model
   - APIKey model
   - Wine model
   - UsageLog model

3. **Schemas** (`app/schemas.py`)
   - UserCreate, UserResponse
   - APIKeyCreate, APIKeyResponse
   - Token schemas

4. **Authentication** (`app/main.py`)
   - POST /register
   - POST /token
   - API key generation

5. **Migration** (`app/migrate.py`)
   - Import wines from CSV to PostgreSQL

### Test Phase 1
```bash
docker-compose up -d --build
docker exec wine-api-saas-api-1 python -m app.migrate --import
curl -H "X-API-Key: dev-api-key-change-me" "http://localhost:8000/wines/stats"
```

---

## Phase 2: SaaS Features ✅

**Goal:** Usage tracking, rate limiting, API tiers

### Implementation

1. **Tier System**
   ```python
   TIER_LIMITS = {
       "free": {"monthly_limit": 1000, "rate_limit": 60},
       "pro": {"monthly_limit": 50000, "rate_limit": 300},
       "enterprise": {"monthly_limit": 1000000, "rate_limit": 1000},
   }
   ```

2. **Usage Tracking Middleware**
   - Log all API calls
   - Track response time
   - Store in UsageLog table

3. **Rate Limiting**
   - Per-API-key rate limiting
   - Monthly limit enforcement

---

## Phase 3: Frontend ✅

**Goal:** User-facing web interface

### Implementation

1. **Next.js Setup**
   ```bash
   npx create-next-app@latest frontend
   ```

2. **Pages Created**
   - `/` - Landing page with hero, features, pricing
   - `/login` - User login
   - `/register` - User registration
   - `/dashboard` - User dashboard with API key management

3. **API Client** (`frontend/lib/api.ts`)
   - Axios wrapper with auth headers

---

## Phase 4: Production Ready ✅

**Goal:** Performance and reliability

### Implementation

1. **Redis Caching** (`app/cache.py`)
   - Cache wine queries
   - Cache statistics
   - Invalidation logic

2. **Celery Tasks** (`app/tasks.py`)
   - Async data import
   - Webhook delivery
   - Email sending

3. **Email Service** (`app/email.py`)
   - Welcome emails
   - Verification
   - Usage alerts

4. **API Versioning**
   - `/v1` prefix
   - `/version` endpoint
   - `/health` endpoint

---

## Phase 5: DevOps & Deployment ✅

**Goal:** CI/CD and deployment automation

### CI/CD Pipeline

| Job | Description |
|-----|-------------|
| lint | ruff, black |
| test | pytest (SQLite) |
| build | Docker multi-platform |
| push | GitHub Container Registry |
| deploy-staging | On push to develop |
| deploy-production | On tag push to main |

### Running Locally

```bash
# Docker Compose (recommended)
docker-compose up -d

# Manual
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker Commands

```bash
# Build
docker build -t wine-api .

# Run
docker run -p 8000:8000 wine-api

# Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

---

## Phase 6: Advanced Features ✅

**Goal:** Enterprise features

### Implementation

1. **Webhooks**
   - Webhook model
   - WebhookDelivery model
   - CRUD endpoints
   - HMAC signatures

2. **Analytics**
   - Usage by day/endpoint/status
   - Export to JSON/CSV

3. **Teams**
   - Team model
   - TeamMember model
   - Member management

4. **White-label**
   - WhiteLabelConfig model
   - Custom branding endpoints

---

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Test Configuration

Tests use SQLite in-memory database for speed and isolation:

```python
# tests/conftest.py
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.environ["DATABASE_URL"] = f"sqlite:///{path}"
    yield
```

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wineapi

# Redis
REDIS_URL=redis://localhost:6379/0

# Auth
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-password
```

---

## Code Quality

### Linting
```bash
ruff check app/ tests/
```

### Formatting
```bash
black app/ tests/
```

---

## Adding New Features

1. **Create model** in `app/models.py`
2. **Create schema** in `app/schemas.py`
3. **Add endpoint** in `app/main.py`
4. **Add tests** in `tests/test_api.py`
5. **Run lint and tests**
6. **Commit and push**

---

## Project Summary

All 24 priority items complete:

| Phase | Features |
|-------|----------|
| Phase 1 | PostgreSQL, JWT auth, API keys |
| Phase 2 | Usage tracking, rate limiting, tiers |
| Phase 3 | Next.js frontend |
| Phase 4 | Redis caching, Celery, email |
| Phase 5 | CI/CD, Docker |
| Phase 6 | Webhooks, analytics, teams, white-label |
