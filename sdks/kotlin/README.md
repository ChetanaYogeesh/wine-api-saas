# Wine API Kotlin SDK (Android)

A Kotlin client for the Wine API.

## Installation

### Gradle

```kotlin
dependencies {
    implementation("com.wineapi:wine-api-kt:1.0.0")
}
```

### Maven

```xml
<dependency>
    <groupId>com.wineapi</groupId>
    <artifactId>wine-api-kt</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Quick Start

```kotlin
import com.wineapi.WineAPI

// Initialize with your API key
val api = WineAPI(apiKey = "your-api-key")

// Get all wines
val wines = api.wines.list(limit = 10)

// Get wine by ID
val wine = api.wines.get(id = 1)

// Search wines
val results = api.wines.search(query = "pinot noir")

// Get top rated
val topWines = api.wines.topRated(limit = 5)

// Get regions
val regions = api.regions.list()

// Get varieties
val varieties = api.varieties.list()

// Get statistics
val stats = api.wines.stats()
```

## Authentication

### API Key

```kotlin
val api = WineAPI(apiKey = "your-api-key")
```

### JWT Token

```kotlin
val api = WineAPI.login(
    email = "user@example.com",
    password = "your-password"
)
```

## Examples

### Filtering Wines

```kotlin
// Filter by region
val wines = api.wines.list(region = "Napa Valley")

// Filter by variety
val wines = api.wines.list(variety = "Red Wine")

// Filter by minimum rating
val wines = api.wines.list(minRating = 90.0)

// Combined filters
val wines = api.wines.list(
    region = "Napa Valley",
    variety = "Red Wine",
    minRating = 85.0,
    limit = 20
)
```

### Pagination

```kotlin
// First page
val page1 = api.wines.list(limit = 10, offset = 0)

// Next page
val page2 = api.wines.list(limit = 10, offset = 10)
```

### Error Handling

```kotlin
try {
    val wine = api.wines.get(id = 12345)
} catch (e: NotFoundException) {
    println("Wine not found")
} catch (e: RateLimitException) {
    println("Rate limited, retry after: ${e.retryAfter}")
} catch (e: UnauthorizedException) {
    println("Invalid API key")
} catch (e: WineAPIException) {
    println("API error: ${e.message}")
}
```

## Models

```kotlin
// Wine data class
data class Wine(
    val id: Int,
    val name: String,
    val region: String,
    val variety: String,
    val rating: Double,
    val vintage: Int?,
    val price: Double?,
    val notes: String?
)

// Region data class
data class Region(
    val name: String,
    val wineCount: Int
)

// Variety data class
data class Variety(
    val name: String,
    val wineCount: Int
)

// Statistics data class
data class WineStats(
    val totalWines: Int,
    val averageRating: Double,
    val totalRegions: Int,
    val totalVarieties: Int
)
```

## Coroutines Support

```kotlin
import kotlinx.coroutines.*

// Use suspend functions
suspend fun loadWines() {
    val wines = api.wines.list(region = "Napa Valley")
    println("Found ${wines.size} wines")
}

// Use withContext for background processing
suspend fun loadInBackground() = withContext(Dispatchers.IO) {
    api.wines.list(limit = 100)
}
```

## RxJava Support

```kotlin
import io.reactivex.rxjava3._

// Use Observable
api.wines.observable(region = "Napa Valley")
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { wines -> println("Wines: $wines") },
        { error -> println("Error: $error") }
    )
```

## GraphQL Support

```kotlin
val query = """
{
    wines(limit: 5) {
        id
        name
        region
        rating
    }
}
"""

val result = api.graphql(query = query)
```

## Configuration

```kotlin
val config = WineAPI.Configuration(
    apiKey = "your-api-key",
    baseUrl = "https://api.wineapi.example.com", // Custom domain
    timeout = 30,
    maxRetries = 3
)

val api = WineAPI(configuration = config)
```

## Rate Limiting

```kotlin
val limits = api.rateLimits()
println("Remaining: ${limits.remaining}")
println("Resets at: ${limits.resetAt}")
```

## Android Specific

### Retrofit Integration

```kotlin
// Use with Retrofit
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.wineapi.example.com/")
    .addConverterFactory(WineAPIConverterFactory())
    .build()
```

### OkHttp Interceptor

```kotlin
// Add API key to all requests automatically
val client = OkHttpClient.Builder()
    .addInterceptor(WineAPIInterceptor(apiKey = "your-key"))
    .build()
```

## License

MIT
