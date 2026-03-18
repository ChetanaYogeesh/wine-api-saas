# Release Notes

## Version 0.2.0 - Complete SaaS Platform

**Release Date:** March 18, 2026

This release completes the Wine API SaaS platform with all core features, advanced enterprise capabilities, and a full frontend dashboard.

---

## What's New

### 🚀 Core API Features
- **32,780 Wine Database** - Comprehensive wine data with ratings, tasting notes, regions, and varieties
- **REST API** - Full CRUD operations with pagination, filtering, and search
- **GraphQL API** - Alternative GraphQL interface powered by Strawberry
- **API Key Authentication** - Secure key-based access control
- **Rate Limiting** - Per-tier rate limits (60/300/1000 requests/minute)

### 💳 Payments & Billing (Phase 2)
- **Stripe Integration** - Full subscription management
- **Three Pricing Tiers:**
  - Free: 1,000 requests/month
  - Pro: $29/month, 50,000 requests/month
  - Enterprise: $99/month, 1,000,000 requests/month
- **Invoice History** - View and download past invoices
- **Customer Portal** - Self-service subscription management
- **Usage Alerts** - Email notifications when approaching limits

### 🤖 AI Features (Phase 4)
- **AI Chatbot** - Local LLM-powered assistant via Ollama
  - Supports llama3.2, llama3.1, mistral, codellama, phi3
  - Wine-specific responses with system prompt
  - Rate limited (10 requests/minute)
  - Requires API key authentication
- **Smart Recommendations** - AI-powered wine suggestions based on preferences
- **Similar Wines** - Find wines similar to one you like
- **Price Tracking** - Monitor wine prices over time from multiple retailers

### 🏪 Marketplace (Phase 4)
- **Wine Listings** - Create and manage wine for sale
- **Transactions** - Buy wines through secure transactions
- **Inventory Management** - Track stock levels

### 🔐 Security & Compliance
- **Comprehensive Security Module** (`app/security.py`)
  - Input validation and sanitization
  - SQL injection prevention
  - XSS protection
  - IDOR protection
  - Rate limiting
  - Security event logging
- **HMAC Webhook Signatures** - Verify webhook authenticity
- **Secure Password Handling** - bcrypt hashing
- **Security Headers** - XSS-Protection, X-Frame-Options, HSTS

### 👥 Enterprise Features (Phase 3)
- **Team Management** - Create teams, add members, assign roles
- **White-Label** - Custom branding with company logo, colors, domain
- **Custom Domains** - Host white-label versions on your own domain
- **Webhook Events** - Subscribe to API events with reliable delivery

### 📊 Analytics & Monitoring
- **Usage Analytics** - Detailed dashboards with charts
- **Export** - Download analytics in JSON or CSV format
- **Endpoint Tracking** - See which endpoints are most used
- **Response Time Metrics** - Monitor API performance

### 📱 Mobile SDKs (Phase 3)
- **Python SDK** - Full documentation with examples
- **JavaScript/TypeScript SDK** - For Node.js and browsers
- **Swift SDK** - For iOS and macOS apps
- **Kotlin SDK** - For Android and JVM applications

### 🎨 Frontend Dashboard
Complete Next.js 16 dashboard with the following pages:

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/dashboard` | Overview with stats and API key management |
| Analytics | `/analytics` | Usage charts and data export |
| Webhooks | `/webhooks` | CRUD for webhook subscriptions |
| Teams | `/teams` | Team and member management |
| White-label | `/white-label` | Branding configuration |
| Usage Alerts | `/usage-alerts` | Manage notification thresholds |
| Settings | `/settings` | Profile editing, password change, delete account |
| Profile | `/profile` | Account info and API key summary |
| Subscription | `/subscription` | Plan management and billing |
| Playground | `/playground` | API sandbox for testing |
| Chatbot | `/` | AI assistant widget |

### 🔧 Developer Experience
- **API Documentation** - Interactive Swagger UI at `/docs`
- **GraphQL Playground** - Interactive GraphQL IDE at `/graphql`
- **Local LLM Support** - Run chatbot with Ollama locally
- **Docker Support** - One-command deployment with docker-compose

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.12 |
| Database | PostgreSQL + SQLAlchemy |
| Cache | Redis |
| Frontend | Next.js 16 + React 18 |
| Auth | JWT + python-jose + bcrypt |
| Payments | Stripe |
| AI | Ollama (local LLM) |
| Rate Limiting | slowapi |
| GraphQL | Strawberry |

---

## Breaking Changes

None. This release is additive.

---

## Deprecations

None.

---

## Migration Guide

For existing users upgrading from v0.1.0:

1. **New Environment Variables** (optional):
   - `OLLAMA_BASE_URL` - For AI chatbot (defaults to localhost:11434)

2. **Database Updates:**
   ```bash
   # Run migrations to add new tables
   docker exec wine-api-saas-api-1 alembic upgrade head
   ```

3. **Frontend Rebuild:**
   ```bash
   cd frontend && npm install && npm run build
   ```

---

## Bug Fixes

- Fixed chatbot not showing when not authenticated
- Fixed SessionLocal import missing in custom domain middleware
- Fixed ruff lint errors across codebase
- Fixed black formatting issues
- Fixed Next.js 16 SSR issues with chatbot

---

## Contributors

- ChetanaYogeesh

---

## Next Steps

See [TODO.md](./TODO.md) for upcoming features and [PRD.md](./PRD.md) for the product roadmap.

---

## Links

- **Documentation:** [README.md](./README.md)
- **Security:** [SECURITY.md](./SECURITY.md)
- **API Reference:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000
