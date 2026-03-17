# Wine API SDKs

Official client libraries for the Wine API.

## Available SDKs

| Language | Status | Package Manager |
|----------|--------|-----------------|
| [Python](./python/) | ✅ Stable | `pip install wine-api` |
| [JavaScript](./javascript/) | ✅ Stable | `npm install wine-api` |
| [Swift](./swift/) | 🔄 Coming Soon | CocoaPods/SPM |
| [Kotlin](./kotlin/) | 🔄 Coming Soon | Gradle/Maven |

## Quick Links

- [Python SDK](./python/README.md)
- [JavaScript SDK](./javascript/README.md)
- [Swift SDK](./swift/README.md)
- [Kotlin SDK](./kotlin/README.md)

## Feature Matrix

| Feature | Python | JavaScript | Swift | Kotlin |
|---------|--------|------------|-------|--------|
| REST API | ✅ | ✅ | ✅ | ✅ |
| GraphQL | ✅ | ✅ | ✅ | ✅ |
| Authentication | ✅ | ✅ | ✅ | ✅ |
| Rate Limiting | ✅ | ✅ | ✅ | ✅ |
| Webhooks | ✅ | ✅ | 🔄 | 🔄 |
| TypeScript | N/A | ✅ | N/A | N/A |
| React Hooks | N/A | ✅ | N/A | N/A |
| RxJava | N/A | N/A | N/A | ✅ |
| Combine | N/A | N/A | ✅ | N/A |

## Installation

### Python
```bash
pip install wine-api
```

### JavaScript/TypeScript
```bash
npm install wine-api
# or
yarn add wine-api
```

### Swift (Coming Soon)
```swift
// Swift Package Manager
.package(url: "https://github.com/wineapi/wine-api-swift.git", from: "1.0.0")
```

### Kotlin (Coming Soon)
```kotlin
implementation("com.wineapi:wine-api-kt:1.0.0")
```

## Basic Usage

```python
# Python
from wine_api import WineAPI
api = WineAPI(api_key="your-key")
wines = api.wines.list(limit=10)
```

```javascript
// JavaScript
import { WineAPI } from 'wine-api';
const api = new WineAPI({ apiKey: 'your-key' });
const wines = await api.wines.list({ limit: 10 });
```

```swift
// Swift
import WineAPI
let api = WineAPI(apiKey: "your-key")
let wines = try await api.wines.list(limit: 10)
```

```kotlin
// Kotlin
val api = WineAPI(apiKey = "your-key")
val wines = api.wines.list(limit = 10)
```

## Support

- GitHub Issues: https://github.com/ChetanaYogeesh/wine-api-saas/issues
- Email: support@wineapi.example.com

## License

MIT
