# Car Trends Analysis Tool - API Documentation

## Overview

The Car Trends Analysis Tool provides a RESTful API for accessing car market data, trends, and analytics. The API is built with FastAPI and provides comprehensive endpoints for managing listings, trends, and analytics.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Endpoints

### Authentication

#### POST /auth/login
Login to get an access token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### GET /auth/me
Get current user information.

**Response:**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "last_login": "2023-01-01T00:00:00Z"
}
```

### Listings

#### GET /listings
Get car listings with optional filters.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Number of records to return (default: 100, max: 1000)
- `platform` (string): Filter by platform (facebook, craigslist, mercadolibre)
- `make` (string): Filter by car make
- `model` (string): Filter by car model
- `min_price` (float): Minimum price filter
- `max_price` (float): Maximum price filter
- `min_year` (int): Minimum year filter
- `max_year` (int): Maximum year filter
- `condition` (string): Filter by condition (new, used, certified, salvage)
- `days_back` (int): Number of days back to search (default: 30)

**Response:**
```json
[
  {
    "id": "string",
    "platform": "facebook",
    "external_id": "string",
    "title": "string",
    "description": "string",
    "make": "string",
    "model": "string",
    "year": 2020,
    "price": 25000.00,
    "currency": "MXN",
    "condition": "used",
    "mileage": 50000,
    "location": "string",
    "url": "string",
    "images": ["string"],
    "views": 100,
    "likes": 10,
    "comments": 5,
    "saves": 2,
    "shares": 1,
    "engagement_score": 150.0,
    "posted_date": "2023-01-01T00:00:00Z",
    "scraped_at": "2023-01-01T00:00:00Z",
    "is_active": true,
    "is_duplicate": false
  }
]
```

#### GET /listings/{listing_id}
Get a specific listing by ID.

#### GET /listings/platform/{platform}
Get listings from a specific platform.

#### GET /listings/top/engagement
Get top listings by engagement score.

#### GET /listings/stats/summary
Get listings summary statistics.

### Trends

#### GET /trends
Get market trends with optional filters.

**Query Parameters:**
- `skip` (int): Number of records to skip
- `limit` (int): Number of records to return
- `make` (string): Filter by car make
- `model` (string): Filter by car model
- `days_back` (int): Number of days back to search

**Response:**
```json
[
  {
    "id": "string",
    "make": "string",
    "model": "string",
    "date": "2023-01-01",
    "total_listings": 10,
    "avg_price": 25000.00,
    "min_price": 20000.00,
    "max_price": 30000.00,
    "total_views": 1000,
    "total_likes": 100,
    "total_comments": 50,
    "total_saves": 20,
    "total_shares": 10,
    "engagement_score": 1500.0,
    "price_change_pct": 5.2,
    "listing_change_pct": -2.1,
    "engagement_change_pct": 10.5
  }
]
```

#### GET /trends/{make}/{model}
Get trends for a specific make and model.

#### GET /trends/top/engagement
Get top trends by engagement score.

#### GET /trends/stats/summary
Get trends summary statistics.

### Analytics

#### GET /analytics/top-cars
Get top cars by engagement metrics.

**Query Parameters:**
- `limit` (int): Number of cars to return (default: 20)
- `days_back` (int): Number of days back to search (default: 30)

**Response:**
```json
[
  {
    "make": "Toyota",
    "model": "Camry",
    "total_listings": 15,
    "avg_price": 25000.00,
    "total_views": 5000,
    "total_likes": 500,
    "total_comments": 100,
    "total_saves": 50,
    "total_shares": 25,
    "engagement_score": 6500.0
  }
]
```

#### GET /analytics/price-trends
Get price trends over time.

**Query Parameters:**
- `make` (string): Filter by car make
- `model` (string): Filter by car model
- `days_back` (int): Number of days back to search

#### GET /analytics/market-share
Get market share analysis.

**Query Parameters:**
- `days_back` (int): Number of days back to search
- `by` (string): Group by 'make' or 'model' (default: make)

#### GET /analytics/engagement-analysis
Get engagement analysis across platforms.

#### GET /analytics/listing-frequency
Get listing frequency analysis.

#### GET /analytics/dashboard-summary
Get comprehensive dashboard summary.

### Scrapers

#### POST /scrapers/trigger
Trigger scraping for all platforms or a specific platform.

**Query Parameters:**
- `platform` (string, optional): Platform to scrape (facebook, craigslist, mercadolibre)

**Response:**
```json
{
  "message": "Scraping triggered for all platforms",
  "status": "started"
}
```

#### GET /scrapers/status
Get current scraping status.

**Response:**
```json
[
  {
    "id": "string",
    "platform": "facebook",
    "started_at": "2023-01-01T00:00:00Z",
    "completed_at": "2023-01-01T00:05:00Z",
    "status": "completed",
    "listings_found": 100,
    "listings_processed": 95,
    "listings_new": 20,
    "listings_updated": 75,
    "errors": [],
    "execution_time_seconds": 300
  }
]
```

#### GET /scrapers/history
Get scraping history.

#### GET /scrapers/stats
Get scraping statistics.

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 60 requests per minute per user
- Rate limit headers are included in responses:
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets

## Examples

### Get top cars by engagement
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/analytics/top-cars?limit=10&days_back=30"
```

### Trigger scraping for Facebook Marketplace
```bash
curl -X POST -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/scrapers/trigger?platform=facebook"
```

### Get listings with filters
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/listings?platform=facebook&make=Toyota&min_price=20000&max_price=30000"
```

## SDK Examples

### Python
```python
import requests

# Login
response = requests.post("http://localhost:8000/api/v1/auth/login", data={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["access_token"]

# Get top cars
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/analytics/top-cars", headers=headers)
top_cars = response.json()
```

### JavaScript
```javascript
// Login
const loginResponse = await fetch("http://localhost:8000/api/v1/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: "username=admin&password=admin123"
});
const { access_token } = await loginResponse.json();

// Get top cars
const response = await fetch("http://localhost:8000/api/v1/analytics/top-cars", {
  headers: { "Authorization": `Bearer ${access_token}` }
});
const topCars = await response.json();
```
