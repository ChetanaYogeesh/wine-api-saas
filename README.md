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
- **Subscriptions** - Stripe integration for billing
- **Invoices** - View and download invoices

### Advanced
- **Webhooks** - Event notifications with HMAC signatures
- **Analytics** - Detailed usage dashboards, JSON/CSV export
- **Team Management** - Multi-user teams with roles
- **White-label** - Custom branding and colors
- **GraphQL API** - Alternative GraphQL interface
- **Mobile SDKs** - Python, JavaScript, Swift, Kotlin SDKs
- **Custom Domain** - White-label with custom domains

### AI Features
- **AI Chatbot** - Local LLM-powered assistant (requires Ollama)
- **AI Recommendations** - Smart wine recommendations based on preferences
- **Price Tracking** - Track wine prices over time from multiple retailers
- **Marketplace** - Buy and sell wines through the platform

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.12 |
| Database | PostgreSQL + SQLAlchemy |
| Cache | Redis |
| Frontend | Next.js 16 + React |
| Auth | JWT + python-jose + bcrypt |
| Payments | Stripe |
| AI | Ollama (local LLM) |
| Rate Limiting | slowapi |
| GraphQL | Strawberry |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Ollama (optional, for AI chatbot)

### Run with Docker

```bash
# Clone the repository
git clone https://github.com/ChetanaYogeesh/wine-api-saas.git
cd wine-api-saas

# Start services (includes database reset and wine import)
docker-compose up -d --build

# Or start and reset manually:
docker-compose up -d
docker exec wine-api-saas-api-1 python -m app.migrate --reset
docker exec wine-api-saas-api-1 python -m app.migrate --import
```

### Access the App

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Frontend | http://localhost:3000 |
| GraphQL | http://localhost:8000/graphql |
| Health | http://localhost:8000/health |

### Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

## Frontend Pages

| Route | Description |
|-------|-------------|
| `/` | Homepage with chatbot |
| `/login` | User login |
| `/register` | User registration |
| `/forgot-password` | Password reset |
| `/dashboard` | API key management |
| `/analytics` | Usage analytics |
| `/webhooks` | Webhook management |
| `/teams` | Team management |
| `/white-label` | Branding config |
| `/usage-alerts` | Alert thresholds |
| `/settings` | Profile & password |
| `/profile` | Account info |
| `/subscription` | Billing management |
| `/playground` | API sandbox |

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | User registration |
| POST | `/token` | JWT login |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password |
| POST | `/auth/change-password` | Change password |

### User Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user |
| PUT | `/users/me` | Update profile |
| DELETE | `/users/me` | Delete account |

### API Keys
| Method | Endpoint | Description |
|--------|----------|-------------|
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

### Usage & Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/usage` | Usage statistics |
| GET | `/usage/alerts` | List alerts |
| POST | `/usage/alerts` | Create alert |
| DELETE | `/usage/alerts/{id}` | Delete alert |
| GET | `/analytics` | Detailed analytics |
| GET | `/analytics/export` | Export data |

### Billing
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/subscription` | Get subscription |
| POST | `/subscription/checkout` | Create checkout |
| POST | `/subscription/portal` | Customer portal |
| POST | `/subscription/cancel` | Cancel subscription |
| GET | `/invoices` | List invoices |
| GET | `/pricing` | Pricing tiers |

### Advanced
| Method | Endpoint | Description |
|--------|----------|-------------|
| CRUD | `/webhooks/*` | Webhook management |
| CRUD | `/teams/*` | Team management |
| CRUD | `/white-label` | White-label config |
| GET | `/graphql` | GraphQL API |
| POST | `/chat/chat` | AI Chatbot (requires API key) |

## Local LLM Setup (Optional)

Enable the AI chatbot by running Ollama locally:

```bash
# Install Ollama (macOS/Linux)
brew install ollama

# Start Ollama
ollama serve

# Pull a model (gemma3:4b recommended)
ollama pull gemma3:4b
```

The chatbot is available in the dashboard and requires an API key for authentication. Ask about "API usage" to see your real usage stats!

## API Key Usage

```bash
# Get wines with API key
curl -H "X-API-Key: your-api-key" http://localhost:8000/wines

# Chat with AI assistant
curl -X POST -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What is a good red wine?"}]}' \
  http://localhost:8000/chat/chat
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection | postgresql://postgres:postgres@localhost:5432/wineapi |
| REDIS_URL | Redis connection | redis://localhost:6379/0 |
| SECRET_KEY | JWT signing secret | change-this-to-a-random-secret-key |
| ALLOWED_ORIGINS | CORS origins | * |
| OLLAMA_BASE_URL | Ollama server URL | http://localhost:11434 |
| DOCKER | Set to "true" when running in Docker | - |
| STRIPE_API_KEY | Stripe secret key | - |
| STRIPE_WEBHOOK_SECRET | Stripe webhook secret | - |

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
  -e OLLAMA_BASE_URL=http://host:11434 \
  -e DOCKER=true \
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
│   ├── chat.py              # Ollama chatbot
│   ├── security.py          # Security utilities
│   ├── payments.py          # Stripe integration
│   ├── recommendations.py   # AI recommendations
│   ├── graphql.py           # GraphQL schema
│   ├── migrate.py           # Data migration
│   └── tasks.py             # Celery tasks
├── frontend/
│   ├── app/                 # Next.js pages
│   │   ├── dashboard/
│   │   ├── analytics/
│   │   ├── webhooks/
│   │   ├── teams/
│   │   ├── white-label/
│   │   ├── settings/
│   │   ├── profile/
│   │   ├── subscription/
│   │   └── components/
│   └── lib/api.ts           # API client
├── sdks/                    # Mobile SDK docs
│   ├── python/
│   ├── javascript/
│   ├── swift/
│   └── kotlin/
├── tests/
│   ├── conftest.py          # Test config
│   └── test_api.py          # API tests
├── docker-compose.yml       # Local dev
└── Dockerfile               # Container image
```

## License

MIT
