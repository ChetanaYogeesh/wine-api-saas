# Complete Wine API SaaS Workflow

## Overview

This document details the complete development workflow for building the Wine API SaaS platform from scratch through all 6 phases.

---

## Phase 1: Foundation

### Goals
- PostgreSQL database
- JWT authentication
- User management
- API key management

### Steps

1. **Create database configuration** (`app/database.py`)
   - SQLAlchemy setup
   - PostgreSQL connection
   - Session management

2. **Create SQLAlchemy models** (`app/models.py`)
   - User model
   - APIKey model
   - Wine model
   - UsageLog model

3. **Create Pydantic schemas** (`app/schemas.py`)
   - UserCreate, UserResponse
   - APIKeyCreate, APIKeyResponse
   - Token schemas

4. **Add authentication endpoints** (`app/main.py`)
   - POST /register
   - POST /token
   - API key generation

5. **Create migration tool** (`app/migrate.py`)
   - Import wines from CSV to PostgreSQL

6. **Update docker-compose.yml**
   - Add PostgreSQL service
   - Add health checks

### Test
```bash
docker-compose up -d --build
docker exec wine-api-saas-api-1 python -m app.migrate --import
curl -H "X-API-Key: dev-api-key-change-me" "http://localhost:8000/wines/stats"
```

---

## Phase 2: SaaS Features

### Goals
- Usage tracking
- Rate limiting per user
- API tiers (Free/Pro/Enterprise)

### Steps

1. **Add tier system**
   ```python
   TIER_LIMITS = {
       "free": {"monthly_limit": 1000, "rate_limit": 60},
       "pro": {"monthly_limit": 50000, "rate_limit": 300},
       "enterprise": {"monthly_limit": 1000000, "rate_limit": 1000},
   }
   ```

2. **Add usage tracking middleware**
   - Log all API calls
   - Track response time
   - Store in UsageLog table

3. **Add rate limiting**
   - Per-API-key rate limiting
   - Monthly limit enforcement

4. **Add user endpoints**
   - GET /me
   - GET /usage
   - GET /usage/logs

---

## Phase 3: Frontend

### Goals
- Landing page
- Authentication pages
- User dashboard
- Interactive docs

### Steps

1. **Create Next.js app**
   ```bash
   npx create-next-app@latest frontend
   ```

2. **Create landing page**
   - Hero section
   - Features
   - Pricing
   - CTA buttons

3. **Create auth pages**
   - /login
   - /register
   - JWT token handling

4. **Create dashboard**
   - User profile
   - API key management
   - Usage stats

5. **Create API client** (`frontend/lib/api.ts`)
   - Axios or fetch wrapper
   - Auth headers

---

## Phase 4: Production Ready

### Goals
- Redis caching
- Celery background tasks
- Email service
- API versioning

### Steps

1. **Add Redis caching** (`app/cache.py`)
   - Cache wine queries
   - Cache statistics
   - Invalidation logic

2. **Add Celery tasks** (`app/tasks.py`)
   - Async data import
   - Webhook delivery
   - Email sending

3. **Add email service** (`app/email.py`)
   - Welcome emails
   - Verification
   - Usage alerts

4. **Add API versioning**
   - /v1 prefix
   - /version endpoint
   - /health endpoint

---

## Phase 5: DevOps & Deployment

### Goals
- CI/CD pipeline
- Docker optimization
- Cloud deployment configs

### Steps

1. **Update CI/CD workflow**
   - Add lint (ruff, black)
   - Add test with services
   - Multi-platform build

2. **Create deployment configs**
   - Railway (railway.json)
   - Heroku (app.json, Procfile)
   - DEPLOYMENT.md guide

3. **Docker optimization**
   - Multi-stage builds
   - Smaller base image
   - Non-root user

---

## Phase 6: Advanced Features

### Goals
- Webhooks
- Analytics
- Team management
- White-label

### Steps

1. **Add webhooks**
   - Webhook model
   - WebhookDelivery model
   - CRUD endpoints
   - HMAC signatures

2. **Add analytics**
   - Usage by day/endpoint/status
   - Export to JSON/CSV

3. **Add teams**
   - Team model
   - TeamMember model
   - Member management

4. **Add white-label**
   - WhiteLabelConfig model
   - Custom branding endpoints

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## Docker Commands

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

## Push to GitHub Container Registry

```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_ACTOR --password-stdin

# Tag
docker tag wine-api ghcr.io/chetanayogeesh/wine-api-saas:latest

# Push
docker push ghcr.io/chetanayogeesh/wine-api-saas:latest
```

---

## CI/CD Pipeline

The GitHub Actions workflow:
1. **Lint** - ruff, black
2. **Test** - pytest with PostgreSQL & Redis
3. **Build** - Docker multi-platform
4. **Push** - GitHub Container Registry
5. **Deploy** - Railway/Heroku (on tags)

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

## Summary

All 6 phases complete with:
- ✅ PostgreSQL database (32,780 wines)
- ✅ JWT + API key authentication
- ✅ Usage tracking & rate limiting
- ✅ Next.js frontend
- ✅ Redis caching
- ✅ Celery background tasks
- ✅ Email service
- ✅ Webhooks with HMAC
- ✅ Analytics & export
- ✅ Team management
- ✅ White-label configuration
- ✅ CI/CD with GitHub Actions
- ✅ Docker containerization
