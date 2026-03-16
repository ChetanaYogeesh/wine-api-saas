# Wine API SaaS - Project Documentation

## Overview
A FastAPI-based wine API with 32,780 wine records, featuring search, filtering, pagination, authentication, rate limiting, and Docker containerization.

## Project Structure
```
wine-api-saas/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI endpoints
│   ├── models.py        # Pydantic schemas
│   └── data.py          # CSV data loader
├── tests/
│   ├── conftest.py      # Test fixtures
│   └── test_api.py      # 18 API tests
├── .github/
│   └── workflows/
│       └── ci-cd.yml    # GitHub Actions CI/CD
├── wine-ratings.csv     # 32,780 wines dataset
├── test_data.csv       # 5 sample wines for testing
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Local development setup
├── .env.example        # Environment variables template
└── .env                # Local environment config
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /wines` | List wines with pagination & filters (region, variety, rating) |
| `GET /wines/{id}` | Get single wine by ID |
| `GET /wines/search?q=...` | Full-text search on name and notes |
| `GET /wines/top-rated` | Top rated wines |
| `GET /wines/stats` | Statistics (total wines, avg rating, top region) |
| `GET /regions` | List all wine regions |
| `GET /regions/{region}/wines` | Wines by region |
| `GET /varieties` | List wine varieties |
| `GET /health` | Health check |

## Authentication
All endpoints (except `/` and `/health`) require an API key:
- Header: `X-API-Key`
- Default key: `dev-api-key-change-me` (set in `.env`)

## Rate Limiting
60 requests/minute per IP address

## Running Locally

### Without Docker
```bash
cd wine-api-saas
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### With Docker
```bash
docker build -t wine-api wine-api-saas/
docker run -p 8000:8000 -e API_KEY=your-key wine-api
```

### With Docker Compose
```bash
docker-compose up --build
```

## Testing
```bash
pytest tests/ -v
# 18 tests pass
```

## GitHub Actions CI/CD

The workflow (`.github/workflows/ci-cd.yml`) automatically:
1. Runs pytest on every push/PR
2. Builds and pushes Docker image to GitHub Container Registry

**Image URL:** `ghcr.io/chetanayogeesh/wine-api-saas:latest`

## Pull and Run from GHCR
```bash
docker pull ghcr.io/chetanayogeesh/wine-api-saas:latest
docker run -p 8000:8000 -e API_KEY=your-key ghcr.io/chetanayogeesh/wine-api-saas:latest
```

## Example API Calls
```bash
# List wines
curl -H "X-API-Key: dev-api-key-change-me" \
  "http://localhost:8000/wines?limit=2"

# Search wines
curl -H "X-API-Key: dev-api-key-change-me" \
  "http://localhost:8000/wines/search?q=raspberry"

# Get stats
curl -H "X-API-Key: dev-api-key-change-me" \
  "http://localhost:8000/wines/stats"

# Top rated
curl -H "X-API-Key: dev-api-key-change-me" \
  "http://localhost:8000/wines/top-rated?limit=5"
```

## Environment Variables
```env
API_KEY=your-secret-api-key
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Git Commits
- `6d8bb55` - Initial scaffolding for wine-api FastAPI project
- `c8f1a11` - Add API key auth, rate limiting, and CORS
- `1207a0d` - Add pytest tests for all API endpoints
- `47bc5fa` - Add Docker containerization and CI/CD workflow
- `350621b` - Fix .dockerignore to include wine-ratings.csv
- `2350e1c` - Update CI/CD to push to GitHub Container Registry
