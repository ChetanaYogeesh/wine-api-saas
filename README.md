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
- **GraphQL API** - Alternative GraphQL interface
- **Mobile SDKs** - Python, JavaScript, Swift, Kotlin SDKs
- **Custom Domain** - White-label with custom domains

### Phase 4 Features
- **AI Recommendations** - Smart wine recommendations based on preferences
- **Price Tracking** - Track wine prices over time from multiple retailers
- **Marketplace** - Buy and sell wines through the platform
- **AI Chatbot** - Local LLM-powered assistant (requires Ollama)

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
| GET | `/wines/{id}/prices` | Get price history |
| POST | `/wines/{id}/prices` | Record price |
| GET | `/regions` | List regions |
| GET | `/varieties` | List varieties |

### Recommendations & Preferences
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recommendations/ai` | AI-powered recommendations |
| GET | `/recommendations/similar/{id}` | Similar wines |
| POST | `/preferences` | Set wine preferences |
| GET | `/preferences` | Get wine preferences |

### Marketplace
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/marketplace/listings` | Create listing |
| GET | `/marketplace/listings` | List listings |
| POST | `/marketplace/transactions` | Purchase wine |

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
| GET | `/graphql` | GraphQL API |
| POST | `/chat` | AI Chatbot (requires API key) |

## Local LLM Setup (Optional)

Enable the AI chatbot in the dashboard by running Ollama locally:

```bash
# Install Ollama (macOS/Linux)
brew install ollama

# Start Ollama
ollama serve

# Pull a model (llama3.2 recommended, ~2GB)
ollama pull llama3.2
```

The chatbot is available in the dashboard and requires an API key for authentication.

## API Key Usage

```bash
# Get wines with API key
curl -H "X-API-Key: your-api-key" http://localhost:8000/wines

# Chat with AI assistant
curl -X POST -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What is a good red wine?"}]}' \
  http://localhost:8000/chat
```

## Environment Variables

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
