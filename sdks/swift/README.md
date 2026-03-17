# Wine API Swift SDK (iOS/macOS)

A Swift client for the Wine API.

## Installation

### Swift Package Manager

```swift
dependencies: [
    .package(url: "https://github.com/wineapi/wine-api-swift.git", from: "1.0.0")
]
```

### CocoaPods

```ruby
pod 'WineAPI', '~> 1.0'
```

## Quick Start

```swift
import WineAPI

// Initialize with your API key
let api = WineAPI(apiKey: "your-api-key")

// Get all wines
let wines = try await api.wines.list(limit: 10)

// Get wine by ID
let wine = try await api.wines.get(id: 1)

// Search wines
let results = try await api.wines.search(query: "pinot noir")

// Get top rated
let topWines = try await api.wines.topRated(limit: 5)

// Get regions
let regions = try await api.regions.list()

// Get varieties
let varieties = try await api.varieties.list()

// Get statistics
let stats = try await api.wines.stats()
```

## Authentication

### API Key

```swift
let api = WineAPI(apiKey: "your-api-key")
```

### JWT Token

```swift
let api = try await WineAPI.login(
    email: "user@example.com",
    password: "your-password"
)
```

## Examples

### Filtering Wines

```swift
// Filter by region
let wines = try await api.wines.list(region: "Napa Valley")

// Filter by variety
let wines = try await api.wines.list(variety: "Red Wine")

// Filter by minimum rating
let wines = try await api.wines.list(minRating: 90)

// Combined filters
let wines = try await api.wines.list(
    region: "Napa Valley",
    variety: "Red Wine",
    minRating: 85,
    limit: 20
)
```

### Pagination

```swift
// First page
let page1 = try await api.wines.list(limit: 10, offset: 0)

// Next page
let page2 = try await api.wines.list(limit: 10, offset: 10)
```

### Error Handling

```swift
do {
    let wine = try await api.wines.get(id: 12345)
} catch WineAPIError.notFound {
    print("Wine not found")
} catch WineAPIError.rateLimited(let retryAfter) {
    print("Rate limited, retry after: \(retryAfter)")
} catch WineAPIError.unauthorized {
    print("Invalid API key")
} catch {
    print("API error: \(error)")
}
```

## Models

```swift
// Wine model
struct Wine: Codable {
    let id: Int
    let name: String
    let region: String
    let variety: String
    let rating: Double
    let vintage: Int?
    let price: Double?
    let notes: String?
}

// Region model
struct Region: Codable {
    let name: String
    let wineCount: Int
}

// Variety model
struct Variety: Codable {
    let name: String
    let wineCount: Int
}

// Statistics model
struct WineStats: Codable {
    let totalWines: Int
    let averageRating: Double
    let totalRegions: Int
    let totalVarieties: Int
}
```

## GraphQL Support

```swift
let query = """
{
    wines(limit: 5) {
        id
        name
        region
        rating
    }
}
"""

let result = try await api.graphql(query: query)
```

## Combine Support

```swift
import Combine

// Use publisher for reactive programming
let publisher = api.wines publisher(region: "Napa Valley")

publisher
    .sink(receiveCompletion: { completion in
        if case .failure(let error) = completion {
            print("Error: \(error)")
        }
    }, receiveValue: { wines in
        print("Wines: \(wines)")
    })
```

## Configuration

```swift
let config = WineAPI.Configuration(
    apiKey: "your-api-key",
    baseURL: "https://api.wineapi.example.com", // Custom domain
    timeout: 30,
    maxRetries: 3
)

let api = WineAPI(configuration: config)
```

## Rate Limiting

```swift
let limits = try await api.rateLimits()
print("Remaining: \(limits.remaining)")
print("Resets at: \(limits.resetAt)")
```

## License

MIT
