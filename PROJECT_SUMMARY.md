# Wine API SaaS - Project Documentation

## Overview
A complete Wine API SaaS platform with 32,780 wine records, featuring FastAPI backend, PostgreSQL database, Redis caching, Next.js frontend, JWT authentication, API key management, usage tracking, rate limiting, webhooks, analytics, team management, and white-label configuration.

## Project Structure
```
wine-api-saas/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI endpoints (60+ endpoints)
│   ├── models.py            # SQLAlchemy models (User, Wine, APIKey, etc.)
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # PostgreSQL configuration
│   ├── cache.py             # Redis caching utilities
│   ├── tasks.py             # Celery background tasks
│   ├── email.py             # Email service
│   ├── migrate.py           # Data migration tool
│   └── logging_config.py    # Logging configuration
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Landing page
│   │   ├── login/           # Login page
│   │   ├── register/        # Register page
│   │   └── dashboard/       # User dashboard
│   └── lib/
│       └── api.ts           # API client
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # GitHub Actions CI/CD
├── wine-ratings.csv         # 32,780 wines dataset
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker image
├── docker-compose.yml        # Local development
└── .env.example
```

## API Endpoints

### Authentication
| Endpoint | Description |
|----------|-------------|
| `POST /register` | User registration |
| `POST /token` | JWT login |
| `POST /api-keys` | Create API key |
| `GET /api-keys` | List API keys |
| `DELETE /api-keys/{id}` | Delete API key |

### Wine Data
| Endpoint | Description |
|----------|-------------|
| `GET /wines` | List wines with pagination & filters |
| `GET /wines/{id}` | Get single wine by ID |
| `GET /wines/search` | Full-text search |
| `GET /wines/top-rated` | Top rated wines |
| `GET /wines/stats` | Statistics |
| `GET /regions` | List all wine regions |
| `GET /regions/{region}/wines` | Wines by region |
| `GET /varieties` | List wine varieties |

### User Management
| Endpoint | Description |
|----------|-------------|
| `GET /me` | Get current user |
| `PATCH /me` | Update user profile |
| `GET /usage` | Get usage statistics |
| `GET /usage/logs` | Get usage logs |

### Webhooks
| Endpoint | Description |
|----------|-------------|
| `POST /webhooks` | Create webhook |
| `GET /webhooks` | List webhooks |
| `GET /webhooks/{id}` | Get webhook |
| `PATCH /webhooks/{id}` | Update webhook |
| `DELETE /webhooks/{id}` | Delete webhook |
| `GET /webhooks/{id}/deliveries` | View delivery history |

### Analytics
| Endpoint | Description |
|----------|-------------|
| `GET /analytics` | Detailed analytics |
| `GET /analytics/export` | Export to JSON/CSV |

### Teams
| Endpoint | Description |
|----------|-------------|
| `POST /teams` | Create team |
| `GET /teams` | List teams |
| `GET /teams/{id}` | Get team |
| `PATCH /teams/{id}` | Update team |
| `DELETE /teams/{id}` | Delete team |
| `POST /teams/{id}/members` | Add member |
| `GET /teams/{id}/members` | List members |
| `PATCH /teams/{id}/members/{mid}` | Update member |
| `DELETE /teams/{id}/members/{mid}` | Remove member |

### White-label
| Endpoint | Description |
|----------|-------------|
| `POST /white-label` | Create config |
| `GET /white-label` | Get config |
| `PATCH /white-label` | Update config |
| `DELETE /white-label` | Delete config |

### System
| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /version` | API version |
| `GET /tiers` | Available plans |

## Authentication

Two authentication methods:
1. **JWT Token** (Bearer): For dashboard access
2. **API Key** (X-API-Key header): For API access

## Rate Limiting

| Tier | Monthly Limit | Rate Limit |
|------|---------------|------------|
| Free | 1,000 | 60/min |
| Pro | 50,000 | 300/min |
| Enterprise | 1,000,000 | 1000/min |

## Running Locally

### Without Docker
```bash
cd wine-api-saas
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### With Docker Compose
```bash
docker-compose up --build
```

## Testing
```bash
pytest tests/ -v
```

## GitHub Actions CI/CD

The workflow automatically:
1. Runs linting (ruff, black)
2. Runs tests with PostgreSQL & Redis
3. Builds and pushes Docker image to GitHub Container Registry

**Image URL:** `ghcr.io/chetanayogeesh/wine-api-saas:latest`

## Pull and Run from GHCR
```bash
docker pull ghcr.io/chetanayogeesh/wine-api-saas:latest
docker run -p 8000:8000 ghcr.io/chetanayogeesh/wine-api-saas:latest
```

## Environment Variables
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wineapi
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-password
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.12 |
| Database | PostgreSQL 16 + SQLAlchemy |
| Cache | Redis 7 |
| Frontend | Next.js 14 + React + Tailwind |
| Auth | JWT + python-jose + bcrypt |
| Rate Limiting | slowapi |
| Background Tasks | Celery |
| Email | aiosmtplib |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Registry | GitHub Container Registry |

## Git Commits (Recent)
- `c93f543` - Add advanced features: webhooks, analytics, teams, white-label
- `c6538ba` - Add production features: Redis caching, Celery, email, versioning
- `f749558` - Add Next.js frontend with landing page, auth, and dashboard
- `2431ce9` - Add SaaS features: usage tracking, rate limiting, API tiers
- `6d6da95` - Add PostgreSQL database, JWT auth, and API key management
