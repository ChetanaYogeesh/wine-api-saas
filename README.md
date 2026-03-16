# Wine API SaaS

A production-ready Wine API platform with 32,780 wine records, built with FastAPI, PostgreSQL, and Next.js.

## Features

### Core
- **Wine Data API** - Search, filter, and browse 32,780 wines
- **PostgreSQL Database** - Reliable data storage
- **Redis Caching** - Fast response times
- **JWT Authentication** - Secure user management
- **API Key Management** - Developer-friendly access control

### SaaS Features
- **Usage Tracking** - Monitor API calls per user
- **Rate Limiting** - Per-tier rate limits (Free/Pro/Enterprise)
- **API Tiers** - Flexible pricing plans

### Advanced
- **Webhooks** - Event notifications with HMAC signatures
- **Analytics** - Detailed usage dashboards, JSON/CSV export
- **Team Management** - Multi-user teams with roles
- **White-label** - Custom branding and colors

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

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local development)

### Run with Docker

```bash
# Clone the repository
git clone https://github.com/ChetanaYogeesh/wine-api-saas.git
cd wine-api-saas

# Start services
docker-compose up -d

# Import wine data
docker exec wine-api-saas-api-1 python -m app.migrate --import
```

### Access the App

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Frontend | http://localhost:3000 |
| Health | http://localhost:8000/health |

### Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | User registration |
| POST | `/token` | JWT login |
| POST | `/api-keys` | Create API key |
| GET | `/api-keys` | List API keys |

### Wine Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/wines` | List wines (paginated) |
| GET | `/wines/{id}` | Get single wine |
| GET | `/wines/search` | Search wines |
| GET | `/wines/top-rated` | Top rated wines |
| GET | `/wines/stats` | Wine statistics |
| GET | `/regions` | List regions |
| GET | `/varieties` | List varieties |

### User Features
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/usage` | Usage statistics |
| GET | `/analytics` | Detailed analytics |
| GET | `/analytics/export` | Export data |

### Advanced
| Method | Endpoint | Description |
|--------|----------|-------------|
| CRUD | `/webhooks/*` | Webhook management |
| CRUD | `/teams/*` | Team management |
| CRUD | `/white-label` | White-label config |

## API Key Usage

```bash
# Get wines with API key
curl -H "X-API-Key: your-api-key" http://localhost:8000/wines

# Get stats
curl -H "X-API-Key: your-api-key" http://localhost:8000/wines/stats
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection | postgresql://postgres:postgres@localhost:5432/wineapi |
| REDIS_URL | Redis connection | redis://localhost:6379/0 |
| SECRET_KEY | JWT signing secret | change-this-to-a-random-secret-key |
| ALLOWED_ORIGINS | CORS origins | * |

## Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

## Docker Image

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/chetanayogeesh/wine-api-saas:latest

# Run
docker run -d \
  -e DATABASE_URL=postgresql://user:pass@host:5432/wineapi \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=your-secret-key \
  -p 8000:8000 \
  ghcr.io/chetanayogeesh/wine-api-saas:latest
```

## Project Structure

```
wine-api-saas/
├── app/
│   ├── main.py              # FastAPI endpoints
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database config
│   ├── cache.py             # Redis caching
│   ├── tasks.py             # Celery tasks
│   └── migrate.py           # Data migration
├── frontend/
│   ├── app/                 # Next.js pages
│   └── lib/api.ts           # API client
├── tests/
│   ├── conftest.py         # Test config
│   └── test_api.py         # API tests
├── .github/workflows/       # CI/CD
├── docker-compose.yml      # Local dev
└── Dockerfile              # Container image
```

## License

MIT
