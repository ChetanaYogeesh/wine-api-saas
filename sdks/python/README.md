# Wine API Python SDK

A Python client for the Wine API.

## Installation

```bash
pip install wine-api
```

## Quick Start

```python
from wine_api import WineAPI

# Initialize with your API key
api = WineAPI(api_key="your-api-key")

# Get all wines
wines = api.wines.list(limit=10)

# Get wine by ID
wine = api.wines.get(1)

# Search wines
results = api.wines.search("pinot noir")

# Get top rated
top_wines = api.wines.top_rated(limit=5)

# Get regions
regions = api.regions.list()

# Get varieties
varieties = api.varieties.list()

# Get statistics
stats = api.wines.stats()
```

## Authentication

### API Key Authentication

```python
api = WineAPI(api_key="your-api-key")
```

### JWT Authentication

```python
api = WineAPI(
    email="user@example.com",
    password="your-password"
)
```

## Examples

### Filtering Wines

```python
# Filter by region
wines = api.wines.list(region="Napa Valley")

# Filter by variety
wines = api.wines.list(variety="Red Wine")

# Filter by minimum rating
wines = api.wines.list(min_rating=90)

# Combined filters
wines = api.wines.list(
    region="Napa Valley",
    variety="Red Wine",
    min_rating=85,
    limit=20
)
```

### Pagination

```python
# First page
wines = api.wines.list(limit=10, offset=0)

# Second page
wines = api.wines.list(limit=10, offset=10)
```

### Error Handling

```python
from wine_api import WineAPI
from wine_api.exceptions import (
    WineAPIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError
)

try:
    wine = api.wines.get(12345)
except NotFoundError:
    print("Wine not found")
except RateLimitError as e:
    print(f"Rate limited: {e}")
except AuthenticationError:
    print("Invalid API key")
except WineAPIError as e:
    print(f"API error: {e}")
```

## GraphQL Support

```python
# Use GraphQL endpoint
query = """
{
    wines(limit: 5) {
        id
        name
        region
        rating
    }
}
"""

result = api.graphql(query)
```

## Configuration

```python
api = WineAPI(
    api_key="your-api-key",
    base_url="https://api.wineapi.example.com",  # Custom domain
    timeout=30,
    max_retries=3
)
```

## Rate Limiting

The SDK automatically handles rate limiting. You can check your limits:

```python
limits = api.rate_limits()
print(f"Remaining: {limits.remaining}")
print(f"Resets at: {limits.reset_at}")
```

## Webhooks

```python
from wine_api import WebhookHandler

handler = WebhookHandler(secret="your-webhook-secret")

# Verify webhook signature
event = handler.verify(request)
print(f"Event type: {event.type}")
```

## License

MIT
