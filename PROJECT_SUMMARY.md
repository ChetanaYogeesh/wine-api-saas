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
├── docker-compose.yml       # Local development
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
| `PATCH /teams/{id}/members/{member_id}` | Update member |
| `DELETE /teams/{id}/members/{member_id}` | Remove member |

### White-label
| Endpoint | Description |
|----------|-------------|
| `POST /white-label` | Create config |
| `GET /white-label` | Get config |
| `PATCH /white-label` | Update config |
| `DELETE /white-label` | Delete config |

### Analytics
| Endpoint | Description |
|----------|-------------|
| `GET /analytics` | Get analytics |
| `GET /analytics/export` | Export analytics |

### System
| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /version` | API version |
| `GET /tiers` | Available tiers |

## Features

### Core Features
- 32,780 wine records
- Search and filter by region, variety, rating
- Pagination support
- Redis caching for performance

### Authentication
- JWT-based authentication
- API key management
- User registration and login

### SaaS Features
- Usage tracking per API key
- Rate limiting (Free, Pro, Enterprise tiers)
- Monthly API call limits
- Usage analytics and export

### Advanced Features
- Webhooks with HMAC signatures
- Team management with roles
- White-label configuration
- Analytics dashboard

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.12 |
| Database | PostgreSQL + SQLAlchemy |
| Cache | Redis |
| Frontend | Next.js + React |
| Auth | JWT + python-jose |
| Rate Limiting | slowapi |
| Background Tasks | Celery |
| CI/CD | GitHub Actions |

## Quick Start

### Docker Compose

```bash
git clone https://github.com/ChetanaYogeesh/wine-api-saas.git
cd wine-api-saas
docker-compose up -d
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wineapi
export REDIS_URL=redis://localhost:6379/0

# Run migrations
python -m app.migrate --init --import

# Start server
uvicorn app.main:app --reload
```

## Testing

```bash
pytest tests/ -v
```

**Test Status:** 18 tests passing  
**Test Configuration:** SQLite in-memory database for testing

## Environment Variables

| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL connection string |
| REDIS_URL | Redis connection string |
| SECRET_KEY | JWT signing secret |
| ALLOWED_ORIGINS | CORS origins |
| API_KEY | Default API key for development |

## Docker

### Build
```bash
docker build -t wine-api .
```

### Run
```bash
docker run -p 8000:8000 wine-api
```

### Docker Compose
```bash
docker-compose up -d
```

## License

MIT
