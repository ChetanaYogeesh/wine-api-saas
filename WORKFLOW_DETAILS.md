# Complete Wine API SaaS Workflow

## Table of Contents
1. [Initial Setup](#1-initial-setup)
2. [Project Scaffolding](#2-project-scaffolding)
3. [Data Acquisition](#3-data-acquisition)
4. [API Development](#4-api-development)
5. [Security Implementation](#5-security-implementation)
6. [Testing](#6-testing)
7. [Containerization](#7-containerization)
8. [CI/CD Pipeline](#8-cicd-pipeline)
9. [Publishing to Registry](#9-publishing-to-registry)

---

## 1. Initial Setup

### Step 1.1: Clone Empty Repository
```bash
git clone git@github.com:ChetanaYogeesh/wine-api-saas.git
# SSH failed, used HTTPS instead:
git clone https://github.com/ChetanaYogeesh/wine-api-saas.git
```

### Step 1.2: Navigate to Project
```bash
cd wine-api-saas
```

---

## 2. Project Scaffolding

### Step 2.1: Create Project Structure
```bash
mkdir -p wine-api-saas/app
```

### Step 2.2: Create requirements.txt
```txt
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
```

### Step 2.3: Create main.py (Basic FastAPI App)
```python
from fastapi import FastAPI

app = FastAPI(title="Wine API", version="0.1.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to Wine API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### Step 2.4: Create .gitignore
```txt
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
.env
.pytest_cache/
.DS_Store
```

### Step 2.5: Create Empty __init__.py
```bash
touch app/__init__.py
```

### Step 2.6: Initial Commit
```bash
git add .
git commit -m "Initial scaffolding for wine-api FastAPI project"
```

---

## 3. Data Acquisition

### Step 3.1: Download Wine Data
```bash
wget https://raw.githubusercontent.com/paiml/wine-ratings/refs/heads/main/wine-ratings.csv \
  -O wine-api-saas/wine-ratings.csv
```
- **Result**: 13MB CSV with 32,780 wines

### Step 3.2: Preview Data
```bash
head -5 wine-api-saas/wine-ratings.csv
```
Columns: `name`, `grape`, `region`, `variety`, `rating`, `notes`

---

## 4. API Development

### Step 4.1: Update requirements.txt (Add pandas)
```txt
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
```

### Step 4.2: Create Data Loader (app/data.py)
```python
import pandas as pd
from pathlib import Path
from typing import Optional

DATA_PATH = Path(__file__).parent.parent / "wine-ratings.csv"
_df: Optional[pd.DataFrame] = None

def get_data() -> pd.DataFrame:
    global _df
    if _df is None:
        _df = pd.read_csv(DATA_PATH, index_col=0)
        _df = _df.drop(columns=["grape"], errors="ignore")
        _df["rating"] = pd.to_numeric(_df["rating"], errors="coerce")
    return _df
```

### Step 4.3: Create Pydantic Models (app/models.py)
```python
from pydantic import BaseModel
from typing import Optional

class Wine(BaseModel):
    id: int
    name: str
    region: Optional[str] = None
    variety: Optional[str] = None
    rating: Optional[float] = None
    notes: Optional[str] = None

class WineListResponse(BaseModel):
    wines: list[Wine]
    total: int
    page: int
    limit: int

class WineStats(BaseModel):
    total_wines: int
    avg_rating: float
    top_region: str
    rating_distribution: dict[str, int]
```

### Step 4.4: Implement All Endpoints (app/main.py)

| Endpoint | Description |
|----------|-------------|
| `GET /wines` | List with pagination & filters |
| `GET /wines/{id}` | Single wine |
| `GET /wines/search?q=...` | Full-text search |
| `GET /wines/top-rated` | Top rated |
| `GET /wines/stats` | Statistics |
| `GET /regions` | List regions |
| `GET /regions/{region}/wines` | Wines by region |
| `GET /varieties` | List varieties |

### Step 4.5: Test Endpoints
```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test
curl "http://localhost:8000/wines?limit=2"
curl "http://localhost:8000/wines/stats"
```

---

## 5. Security Implementation

### Step 5.1: Add Security Dependencies
```txt
slowapi>=0.1.9
python-multipart>=0.0.6
```

### Step 5.2: Create .env.example
```env
API_KEY=your-secret-api-key-here
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Step 5.3: Update main.py with Security Features

**API Key Authentication:**
```python
from fastapi.security import APIKeyHeader

security_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(request: Request, api_key: str = Depends(security_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

**Rate Limiting (60 req/min):**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/wines")
@limiter.limit("60/minute")
async def list_wines(request: Request, ...):
```

**CORS Configuration:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 5.4: Test Security
```bash
# Without API key - should fail
curl "http://localhost:8000/wines"
# {"detail":"Invalid API key"}

# With API key - should work
curl -H "X-API-Key: dev-api-key-change-me" "http://localhost:8000/wines"
```

---

## 6. Testing

### Step 6.1: Add Test Dependencies
```txt
pytest>=7.0.0
httpx>=0.24.0
```

### Step 6.2: Create Test Data (test_data.csv)
```csv
,name,grape,region,variety,rating,notes
0,Test Red Wine 2020,Cabernet Sauvignon,Napa Valley,Red Wine,92.0,A test wine with notes of cherry and oak.
1,Test White Wine 2021,Chardonnay,Sonoma,White Wine,88.0,A crisp white wine with apple and citrus notes.
2,Test Rosé 2022,Pinot Noir,Provence,Rose Wine,85.0,Light and refreshing with strawberry flavors.
3,Test Pinot Noir 2019,Pinot Noir,Willamette Valley,Red Wine,95.0,An elegant Pinot with dark fruit and earthy undertones.
4,Test Bordeaux 2018,Merlot,Bordeaux,Red Wine,91.0,A classic Bordeaux with plum and spice.
```

### Step 6.3: Create Test Fixtures (tests/conftest.py)
```python
import os, sys, pytest
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ["API_KEY"] = "test-api-key"

TEST_DATA_PATH = Path(__file__).parent.parent / "test_data.csv"

@pytest.fixture(scope="function")
def reset_data():
    from app import data
    data.DATA_PATH = TEST_DATA_PATH
    data._df = None
    yield
    data._df = None

@pytest.fixture
def client(reset_data):
    from app.main import app
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-api-key"}
```

### Step 6.4: Create Test Cases (tests/test_api.py)
- 18 tests covering all endpoints
- Tests for: pagination, filters, search, auth, errors

### Step 6.5: Run Tests
```bash
pytest tests/ -v
# Result: 18 passed
```

---

## 7. Containerization

### Step 7.1: Create Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV API_KEY=${API_KEY:-dev-api-key-change-me}
ENV ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-*}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 7.2: Create .dockerignore
```txt
__pycache__/
venv/
.env
.git/
tests/
test_data.csv
Dockerfile
docker-compose.yml
.github/
# NOTE: Do NOT exclude wine-ratings.csv!
```

### Step 7.3: Create docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - API_KEY=${API_KEY:-dev-api-key-change-me}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-*}
    volumes:
      - ./wine-ratings.csv:/app/wine-ratings.csv:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Step 7.4: Build and Test Docker Image
```bash
# Build
docker build -t wine-api wine-api-saas/

# Run
docker run -d -p 8000:8000 --name wine-api -e API_KEY=dev-api-key-change-me wine-api

# Test
curl -H "X-API-Key: dev-api-key-change-me" "http://localhost:8000/wines?limit=1"

# Stop
docker stop wine-api && docker rm wine-api
```

---

## 8. CI/CD Pipeline

### Step 8.1: Create GitHub Actions Workflow
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v

  build-and-push:
    runs-on: ubuntu-latest
    needs: test
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
```

---

## 9. Publishing to Registry

### Step 9.1: Tag Image for GHCR
```bash
docker build -t ghcr.io/chetanayogeesh/wine-api-saas:latest wine-api-saas/
```

### Step 9.2: Login to GitHub Container Registry
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u chetanayogeesh --password-stdin
```
- Use GitHub Personal Access Token with `read:packages` and `write:packages` scopes

### Step 9.3: Push to GHCR
```bash
docker push ghcr.io/chetanayogeesh/wine-api-saas:latest
```

### Step 9.4: Verify
- Visit: `https://github.com/users/ChetanaYogeesh/packages/container/wine-api-saas`

---

## Summary

### Commands Run
```bash
# Setup
git clone https://github.com/ChetanaYogeesh/wine-api-saas.git
cd wine-api-saas
mkdir -p app tests .github/workflows

# Dependencies
pip install -r requirements.txt
pip install pytest httpx slowapi python-multipart

# Development
uvicorn app.main:app --reload

# Testing
pytest tests/ -v

# Docker
docker build -t wine-api .
docker run -p 8000:8000 -e API_KEY=your-key wine-api

# Publish
docker tag wine-api ghcr.io/chetanayogeesh/wine-api-saas:latest
docker push ghcr.io/chetanayogeesh/wine-api-saas:latest
```

### Final Deliverables
- **API**: 8 endpoints with auth & rate limiting
- **Tests**: 18 passing tests
- **Container**: 460MB Docker image
- **Registry**: `ghcr.io/chetanayogeesh/wine-api-saas:latest`
- **CI/CD**: GitHub Actions workflow
