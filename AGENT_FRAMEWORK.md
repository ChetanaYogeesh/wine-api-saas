# Wine API SaaS - Project Context

This document provides context for AI agents working on the Wine API SaaS project.

---

## Project Overview

**Wine API SaaS** is a complete API-as-a-Service platform for wine data with:
- 32,780 wine records
- PostgreSQL database
- Redis caching
- Next.js frontend
- JWT + API key authentication
- Usage tracking & rate limiting
- Webhooks, analytics, teams, white-label

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.12 |
| Database | PostgreSQL + SQLAlchemy |
| Cache | Redis |
| Frontend | Next.js + React + Tailwind |
| Auth | JWT + python-jose |
| Rate Limiting | slowapi |
| Background Tasks | Celery |
| CI/CD | GitHub Actions |
| Registry | ghcr.io |

---

## Key Files

```
app/
├── main.py              # 60+ API endpoints
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── database.py          # DB configuration
├── cache.py             # Redis caching
├── tasks.py             # Celery tasks
└── email.py             # Email service

frontend/
├── app/
│   ├── page.tsx         # Landing page
│   ├── login/           # Login
│   ├── register/        # Registration
│   └── dashboard/       # User dashboard
└── lib/api.ts           # API client
```

---

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /token` - JWT login
- `POST /api-keys` - Create API key
- `GET /api-keys` - List API keys

### Wine Data
- `GET /wines` - List with pagination/filters
- `GET /wines/{id}` - Single wine
- `GET /wines/search` - Search
- `GET /wines/stats` - Statistics
- `GET /regions` - Wine regions
- `GET /varieties` - Wine varieties

### User Features
- `GET /usage` - Usage statistics
- `GET /analytics` - Detailed analytics
- `GET /analytics/export` - Export data

### Advanced
- `/webhooks/*` - Webhook management
- `/teams/*` - Team management
- `/white-label` - White-label config

---

## Running Locally

```bash
# Docker Compose (recommended)
docker-compose up --build

# Manual
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Testing

```bash
pytest tests/ -v
```

---

## Environment Variables

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wineapi
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000
```

---

## CI/CD

GitHub Actions workflow at `.github/workflows/ci-cd.yml`:
1. Lint (ruff, black)
2. Test (PostgreSQL + Redis)
3. Build & push to ghcr.io

**Image:** `ghcr.io/chetanayogeesh/wine-api-saas:latest`

---

## Development Guidelines

- Use type hints
- Follow existing code patterns
- Add tests for new endpoints
- Use pydantic for validation
- Use SQLAlchemy for DB operations
