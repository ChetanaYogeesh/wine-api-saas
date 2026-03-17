# Security Documentation

This document outlines the security features and best practices implemented in the Wine API SaaS platform.

## Table of Contents

1. [Authentication](#authentication)
2. [Authorization](#authorization)
3. [Input Validation](#input-validation)
4. [Security Headers](#security-headers)
5. [Rate Limiting](#rate-limiting)
6. [Security Event Logging](#security-event-logging)
7. [Data Sanitization](#data-sanitization)
8. [IDOR Protection](#idor-protection)
9. [Database Security](#database-security)
10. [Chat Endpoint Security](#chat-endpoint-security)

---

## Authentication

### JWT Authentication
- Tokens are signed using `HS256` algorithm
- Configurable token expiration (default: 30 minutes)
- Secure password hashing with bcrypt

```python
# Password hashing
bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
```

### API Key Authentication
- API keys are required for all wine data endpoints
- Keys are validated against the database on each request
- Inactive keys are rejected

### OAuth2
- OAuth2PasswordBearer for user authentication
- Token validation on every protected endpoint

---

## Authorization

### User Data Access
- Users can only access their own data
- API keys are linked to specific users
- Team-based access control for Enterprise tier

### Marketplace Authorization
- Users cannot purchase their own listings
- Transaction validation ensures proper ownership

```python
# From app/main.py
if listing.seller_id == current_user.id:
    log_security_event(
        event_type="SELF_PURCHASE_ATTEMPT",
        user_id=current_user.id,
        details={"listing_id": listing.id},
    )
    raise HTTPException(status_code=400, detail="Cannot purchase your own listing")
```

---

## Input Validation

All user inputs are validated using the `app/security.py` module.

### Validation Functions

| Function | Description | Bounds |
|----------|-------------|--------|
| `validate_price()` | Validates price values | 0 - 100,000 |
| `validate_rating()` | Validates rating values | 0.0 - 5.0 |
| `validate_quantity()` | Validates quantity | 1 - 10,000 |
| `validate_limit()` | Validates pagination limit | 1 - 100 |
| `validate_offset()` | Validates pagination offset | 0 - 10,000 |
| `validate_id()` | Validates ID values | >= 1 |
| `validate_currency()` | Validates currency codes | USD, EUR, GBP, etc. |
| `validate_url()` | Validates URL format | Max 500 chars |
| `validate_email()` | Validates email format | RFC 5322 |

### Code Example

```python
from app.security import validate_price, validate_rating

try:
    price = validate_price(user_input_price)
    rating = validate_rating(user_input_rating)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

---

## Security Headers

All responses include security headers to protect against common attacks.

### Implemented Headers

```python
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-XSS-Protection"] = "1; mode=block"
response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
```

### Header Descriptions

| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | nosniff | Prevents MIME-type sniffing |
| X-Frame-Options | DENY | Prevents clickjacking |
| X-XSS-Protection | 1; mode=block | XSS filtering |
| Strict-Transport-Security | max-age=31536000 | Enforces HTTPS |
| Referrer-Policy | strict-origin-when-cross-origin | Controls referrer info |

---

## Rate Limiting

Rate limiting is implemented using `slowapi` with tier-based limits.

### Tier Limits

| Tier | Monthly Requests | Rate Limit |
|------|-----------------|------------|
| Free | 1,000 | 60/min |
| Pro | 50,000 | 300/min |
| Enterprise | 1,000,000 | 1,000/min |

### Implementation

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/wines")
@limiter.limit("60/minute")
async def get_wines(request: Request, ...):
    ...
```

---

## Security Event Logging

All security-relevant events are logged using the `log_security_event()` function.

### Events Logged

| Event | Description |
|-------|-------------|
| `UNAUTHORIZED_ACCESS_ATTEMPT` | User tried to access another user's data |
| `SELF_PURCHASE_ATTEMPT` | User tried to buy their own listing |
| `API_KEY_MISMATCH` | API key ownership validation failed |
| `LISTING_CREATED` | New marketplace listing created |
| `TRANSACTION_CREATED` | New transaction created |

### Code Example

```python
from app.security import log_security_event

log_security_event(
    event_type="UNAUTHORIZED_ACCESS_ATTEMPT",
    user_id=current_user.id,
    details={
        "resource_type": "wine_preference",
        "resource_owner_id": resource_user_id,
        "attempted_by": current_user.id,
    },
    ip_address=request.client.host,
)
```

---

## Data Sanitization

All user inputs are sanitized before storage to prevent XSS and injection attacks.

### Sanitization Functions

| Function | Description | Max Length |
|----------|-------------|------------|
| `sanitize_string()` | Removes control characters | 500 (configurable) |
| `sanitize_text()` | Removes control characters | 5000 |
| `validate_url()` | Validates and truncates URLs | 500 |

### Implementation

```python
from app.security import sanitize_string, sanitize_text

# Sanitize string input
name = sanitize_string(user_input, max_length=255)

# Sanitize text/description
description = sanitize_text(user_input)

# Validate URL
url = validate_url(user_url)  # Raises ValidationError if invalid
```

### Character Removal

```python
import re

def sanitize_string(value: Optional[str], max_length: int = 500) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    # Remove control characters
    value = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', value)
    return value[:max_length]
```

---

## IDOR Protection

Insecure Direct Object Reference (IDOR) protection ensures users can only access their own resources.

### Implementation

```python
from app.security import check_resource_ownership

def update_user_preference(
    preference_id: int,
    current_user: User,
    db: Session
):
    preference = db.query(WinePreference).get(preference_id)
    
    # Check ownership
    if not check_resource_ownership(
        db,
        resource_user_id=preference.user_id,
        current_user_id=current_user.id,
        resource_type="wine_preference"
    ):
        raise HTTPException(status_code=403, detail="Access denied")
```

---

## Database Security

### SQL Injection Prevention
- All queries use SQLAlchemy ORM with parameterized queries
- No raw SQL queries with user input

### Query Example (Safe)

```python
# Safe - uses parameterized query
wine = db.query(Wine).filter(Wine.id == wine_id).first()

# Safe - uses ilike with parameterization
query = query.filter(Wine.region.ilike(f"%{region}%"))
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)
```

---

## Security Utilities Module

The `app/security.py` module provides all security-related utilities:

```python
from app.security import (
    # Validation
    validate_price,
    validate_rating,
    validate_quantity,
    validate_limit,
    validate_offset,
    validate_id,
    validate_currency,
    validate_email,
    validate_url,
    validate_pagination,
    
    # Sanitization
    sanitize_string,
    sanitize_text,
    
    # Authorization
    check_resource_ownership,
    validate_api_key_ownership,
    
    # Logging
    log_security_event,
    
    # Marketplace
    validate_marketplace_transaction,
    sanitize_marketplace_listing_params,
)
```

---

## Testing Security

Run the test suite to verify security implementations:

```bash
pytest tests/ -v
```

All 18 tests pass with the security enhancements in place.

---

## Best Practices Summary

1. **Always validate input** - Use validation functions before processing
2. **Sanitize output** - Clean data before displaying or storing
3. **Log security events** - Track suspicious activities
4. **Use security headers** - Protect against common attacks
5. **Implement rate limiting** - Prevent abuse
6. **Check authorization** - Verify ownership before access
7. **Hash passwords** - Use bcrypt for password storage
8. **Use HTTPS** - Enable TLS in production

---

## Chat Endpoint Security

The `/chat` endpoint provides AI-powered chatbot functionality using a local LLM (Ollama). It includes additional security measures:

### Authentication
- **API Key Required** - All requests must include valid `X-API-Key` header
- Keys are validated against the database and must be active

### Rate Limiting
- **10 requests/minute** - Prevents abuse of AI resources
- Applied per API key

### Input Validation
- Maximum 2000 characters per message
- Maximum 20 messages per request
- Maximum 500 tokens in response
- Temperature must be between 0 and 2

### Model Restrictions
Only whitelisted models are allowed:
- `llama3.2`, `llama3.1`, `llama3`
- `mistral`, `codellama`, `phi3`

### Output Sanitization
- Removes URLs from AI responses
- Removes control characters
- Truncates excessively long responses (max 10000 chars)

### Ollama Security
- Ollama binds to `localhost:11434` only
- Not exposed to public internet
- No external API calls

### Usage

```bash
# Chat request requires API key
curl -X POST http://localhost:8000/chat \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"What pairs well with steak?"}]}'
```

---

**Document Version:** 1.1  
**Last Updated:** March 17, 2026
