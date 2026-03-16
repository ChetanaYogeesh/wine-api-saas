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
| API_KEY | Default API key | No |
| ALLOWED_ORIGINS | CORS origins | No |

## Production Checklist

- [ ] Set strong SECRET_KEY
- [ ] Configure ALLOWED_ORIGINS
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure backup for PostgreSQL
- [ ] Set up Redis persistence
- [ ] Configure rate limiting
- [ ] Enable logging

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
