# Wine API SaaS - Deployment Guide

## Prerequisites
- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+
- Python 3.12

## Local Development

### Quick Start
```bash
# Clone and setup
git clone https://github.com/ChetanaYogeesh/wine-api-saas.git
cd wine-api-saas

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with Docker Compose
docker-compose up -d

# Import data
docker exec wine-api-saas-api-1 python -m app.migrate --import

# Access API
curl http://localhost:8000/health

# Access frontend
open http://localhost:3000
```

### Manual Setup
```bash
# Start PostgreSQL and Redis
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16-alpine
docker run -d -p 6379:6379 redis:7-alpine

# Set environment variables
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wineapi
export REDIS_URL=redis://localhost:6379/0
export SECRET_KEY=your-secret-key

# Run database migrations
python -m app.migrate --init --import

# Start API
uvicorn app.main:app --reload
```

## Deployment Platforms

### Railway

1. **Connect GitHub repository**
2. **Add PostgreSQL plugin** (provisioned automatically)
3. **Add Redis plugin** (provisioned automatically)
4. **Deploy**
```bash
railway init
railway deploy
```

### Render

1. **Connect GitHub repository**
2. **Create PostgreSQL** (Render managed)
3. **Create Redis** (Render managed)
4. **Deploy from GitHub** (auto-deploy on push)

### Heroku

```bash
# Create app
heroku create wine-api-saas

# Add addons
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev

# Set config vars
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_ORIGINS=https://yourdomain.com

# Deploy
git push heroku main
```

### AWS ECS (Advanced)

1. Build and push Docker image to ECR
2. Create ECS cluster
3. Create Task Definition
4. Set environment variables
5. Create Service

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| REDIS_URL | Redis connection string | Yes |
| SECRET_KEY | JWT signing secret | Yes |
| JWT_ALGORITHM | JWT algorithm (default: HS256) | No |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiry (default: 30) | No |
| ALLOWED_ORIGINS | CORS origins | No |
| EMAIL_HOST | SMTP host | No |
| EMAIL_PORT | SMTP port | No |
| EMAIL_USER | SMTP user | No |
| EMAIL_PASSWORD | SMTP password | No |

## Production Checklist

- [x] Set strong SECRET_KEY
- [x] Configure ALLOWED_ORIGINS
- [x] Enable HTTPS
- [x] Set up monitoring
- [x] Configure backup for PostgreSQL
- [x] Set up Redis persistence
- [x] Configure rate limiting
- [x] Enable logging

## Docker Production

```bash
# Build
docker build -t wine-api:latest .

# Run
docker run -d \
  -e DATABASE_URL=postgresql://user:pass@host:5432/wineapi \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=your-secret-key \
  -p 8000:8000 \
  wine-api:latest
```

## GitHub Container Registry

### Pull and Run
```bash
# Pull
docker pull ghcr.io/chetanayogeesh/wine-api-saas:latest

# Run
docker run -d \
  -e DATABASE_URL=postgresql://user:pass@host:5432/wineapi \
  -e REDIS_URL=redis://host:6379/0 \
  -e SECRET_KEY=your-secret-key \
  -p 8000:8000 \
  ghcr.io/chetanayogeesh/wine-api-saas:latest
```

### Push New Version
```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_ACTOR --password-stdin

# Tag
docker tag wine-api:latest ghcr.io/chetanayogeesh/wine-api-saas:v1.0.0

# Push
docker push ghcr.io/chetanayogeesh/wine-api-saas:v1.0.0
```

## Kubernetes (Optional)

See `k8s/` directory for Kubernetes manifests.

```bash
kubectl apply -f k8s/
```

## Monitoring

Recommended services:
- **Sentry** - Error tracking
- **DataDog** - Full observability  
- **LogRocket** - Frontend monitoring
- **UptimeRobot** - Uptime monitoring

## API Endpoints Reference

### Authentication
- `POST /register` - User registration
- `POST /token` - JWT login
- `POST /api-keys` - Create API key
- `GET /api-keys` - List API keys

### Wine Data
- `GET /wines` - List wines
- `GET /wines/{id}` - Get wine
- `GET /wines/search` - Search
- `GET /wines/stats` - Statistics
- `GET /regions` - Regions
- `GET /varieties` - Varieties

### User
- `GET /me` - Current user
- `GET /usage` - Usage stats
- `GET /analytics` - Detailed analytics
- `GET /analytics/export` - Export data

### Advanced
- `/webhooks/*` - Webhook management
- `/teams/*` - Team management
- `/white-label` - White-label config
