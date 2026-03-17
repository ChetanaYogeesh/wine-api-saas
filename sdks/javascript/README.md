# Wine API JavaScript SDK

A JavaScript/TypeScript client for the Wine API.

## Installation

```bash
npm install wine-api
```

## Quick Start

```javascript
import { WineAPI } from 'wine-api';

// Initialize with your API key
const api = new WineAPI({ apiKey: 'your-api-key' });

// Get all wines
const wines = await api.wines.list({ limit: 10 });

// Get wine by ID
const wine = await api.wines.get(1);

// Search wines
const results = await api.wines.search('pinot noir');

// Get top rated
const topWines = await api.wines.topRated({ limit: 5 });

// Get regions
const regions = await api.regions.list();

// Get varieties
const varieties = await api.varieties.list();

// Get statistics
const stats = await api.wines.stats();
```

## Authentication

### API Key

```javascript
const api = new WineAPI({ apiKey: 'your-api-key' });
```

### JWT Token

```javascript
const api = new WineAPI({
    email: 'user@example.com',
    password: 'your-password'
});
```

## Examples

### Filtering Wines

```javascript
// Filter by region
const wines = await api.wines.list({ region: 'Napa Valley' });

// Filter by variety
const wines = await api.wines.list({ variety: 'Red Wine' });

// Filter by minimum rating
const wines = await api.wines.list({ minRating: 90 });

// Combined filters
const wines = await api.wines.list({
    region: 'Napa Valley',
    variety: 'Red Wine',
    minRating: 85,
    limit: 20
});
```

### Pagination

```javascript
// First page
const page1 = await api.wines.list({ limit: 10, offset: 0 });

// Next page
const page2 = await api.wines.list({ limit: 10, offset: 10 });
```

### Error Handling

```javascript
import { WineAPI, WineAPIError, AuthenticationError, RateLimitError } from 'wine-api';

try {
    const wine = await api.wines.get(12345);
} catch (error) {
    if (error instanceof NotFoundError) {
        console.log('Wine not found');
    } else if (error instanceof RateLimitError) {
        console.log('Rate limited, retry after:', error.retryAfter);
    } else if (error instanceof AuthenticationError) {
        console.log('Invalid API key');
    } else {
        console.log('API error:', error.message);
    }
}
```

## TypeScript Support

```typescript
import { WineAPI, Wine, WineListResponse } from 'wine-api';

const api = new WineAPI({ apiKey: 'your-api-key' });

const wines: Wine[] = await api.wines.list({ limit: 10 });
const wine: Wine | null = await api.wines.get(1);
```

## GraphQL Support

```javascript
const query = `
{
    wines(limit: 5) {
        id
        name
        region
        rating
    }
}
`;

const result = await api.graphql(query);
```

## React Hooks

```javascript
import { useWineAPI } from 'wine-api/react';

function WineList() {
    const { wines, loading, error } = useWineAPI({
        region: 'Napa Valley',
        limit: 10
    });

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;

    return (
        <ul>
            {wines.map(wine => (
                <li key={wine.id}>{wine.name}</li>
            ))}
        </ul>
    );
}
```

## Rate Limiting

```javascript
const limits = await api.rateLimits();
console.log(`Remaining: ${limits.remaining}`);
console.log(`Resets at: ${limits.resetAt}`);
```

## Configuration

```javascript
const api = new WineAPI({
    apiKey: 'your-api-key',
    baseUrl: 'https://api.wineapi.example.com', // Custom domain
    timeout: 30000,
    retries: 3
});
```

## Node.js Usage

```javascript
const { WineAPI } = require('wine-api');
```

## Browser Usage

```html
<script src="https://cdn.wineapi.example.com/sdk.js"></script>
<script>
    const api = new WineAPI({ apiKey: 'your-api-key' });
</script>
```

## License

MIT
