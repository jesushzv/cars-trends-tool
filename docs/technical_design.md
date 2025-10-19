# Car Trends Analysis Tool - Technical Design

## System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Scrapers      │
                       │ (Playwright)    │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  External APIs  │
                       │ FB, CL, ML      │
                       └─────────────────┘
```

### Technology Stack
- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Frontend**: React 18, TypeScript, Chart.js, Tailwind CSS
- **Database**: PostgreSQL 15
- **Scraping**: Playwright, BeautifulSoup4
- **Scheduling**: APScheduler
- **Deployment**: Docker, Docker Compose
- **Authentication**: JWT tokens

## Data Models

### Core Entities

#### Listing
```python
class Listing:
    id: UUID
    platform: str  # 'facebook', 'craigslist', 'mercadolibre'
    external_id: str  # Platform-specific ID
    title: str
    description: str
    make: str
    model: str
    year: int
    price: Decimal
    currency: str
    condition: str  # 'new', 'used', 'certified'
    mileage: int
    location: str
    url: str
    images: List[str]
    
    # Engagement metrics
    views: int
    likes: int
    comments: int
    saves: int
    shares: int
    
    # Metadata
    posted_date: datetime
    scraped_at: datetime
    is_active: bool
    is_duplicate: bool
```

#### Trend
```python
class Trend:
    id: UUID
    make: str
    model: str
    date: date
    
    # Aggregated metrics
    total_listings: int
    avg_price: Decimal
    total_views: int
    total_likes: int
    total_comments: int
    engagement_score: float
    
    # Calculated metrics
    price_change_pct: float
    listing_change_pct: float
    engagement_change_pct: float
```

#### ScrapingSession
```python
class ScrapingSession:
    id: UUID
    platform: str
    started_at: datetime
    completed_at: datetime
    status: str  # 'running', 'completed', 'failed'
    listings_found: int
    listings_processed: int
    errors: List[str]
```

## API Design

### Authentication Endpoints
```
POST /auth/login
POST /auth/refresh
POST /auth/logout
```

### Data Endpoints
```
GET /api/listings
GET /api/listings/{id}
GET /api/trends
GET /api/trends/{make}/{model}
GET /api/analytics/top-cars
GET /api/analytics/price-trends
GET /api/analytics/market-share
```

### Management Endpoints
```
POST /api/scrapers/trigger
GET /api/scrapers/status
GET /api/scrapers/history
```

## Scraping Architecture

### Scraper Base Class
```python
class BaseScraper:
    def __init__(self, platform: str):
        self.platform = platform
        self.browser = None
    
    async def scrape_listings(self, location: str) -> List[Listing]:
        """Main scraping method"""
        pass
    
    def extract_car_info(self, listing_html: str) -> dict:
        """Extract car details from HTML"""
        pass
    
    def extract_engagement(self, listing_html: str) -> dict:
        """Extract engagement metrics"""
        pass
    
    def normalize_car_model(self, make: str, model: str) -> tuple:
        """Normalize car make/model names"""
        pass
```

### Platform-Specific Scrapers

#### Facebook Marketplace Scraper
- **Challenges**: Requires authentication, dynamic content
- **Strategy**: Use Playwright with authenticated session
- **Engagement**: Views, likes, comments, shares
- **Rate Limiting**: 2-3 second delays between requests

#### Craigslist Scraper
- **Challenges**: Simple HTML, but location filtering
- **Strategy**: Direct HTTP requests with BeautifulSoup
- **Engagement**: Limited (no public metrics)
- **Rate Limiting**: 1 second delays

#### Mercado Libre Scraper
- **Challenges**: Dynamic content, Spanish language
- **Strategy**: Playwright for dynamic content
- **Engagement**: Views, likes, questions
- **Rate Limiting**: 2 second delays

## Database Schema

### Tables
```sql
-- Listings table
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(20) NOT NULL,
    external_id VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    make VARCHAR(50),
    model VARCHAR(50),
    year INTEGER,
    price DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'MXN',
    condition VARCHAR(20),
    mileage INTEGER,
    location VARCHAR(100),
    url TEXT NOT NULL,
    images TEXT[], -- Array of image URLs
    
    -- Engagement metrics
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    
    -- Metadata
    posted_date TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    is_duplicate BOOLEAN DEFAULT FALSE,
    
    UNIQUE(platform, external_id)
);

-- Trends table
CREATE TABLE trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    
    -- Aggregated metrics
    total_listings INTEGER DEFAULT 0,
    avg_price DECIMAL(12,2),
    total_views INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    engagement_score DECIMAL(10,2),
    
    -- Calculated metrics
    price_change_pct DECIMAL(5,2),
    listing_change_pct DECIMAL(5,2),
    engagement_change_pct DECIMAL(5,2),
    
    UNIQUE(make, model, date)
);

-- Scraping sessions
CREATE TABLE scraping_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(20) NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running',
    listings_found INTEGER DEFAULT 0,
    listings_processed INTEGER DEFAULT 0,
    errors TEXT[]
);
```

### Indexes
```sql
-- Performance indexes
CREATE INDEX idx_listings_platform_scraped ON listings(platform, scraped_at);
CREATE INDEX idx_listings_make_model ON listings(make, model);
CREATE INDEX idx_listings_price ON listings(price);
CREATE INDEX idx_trends_make_model_date ON trends(make, model, date);
CREATE INDEX idx_trends_date ON trends(date);
```

## Security Considerations

### Authentication
- JWT tokens with 24-hour expiration
- Refresh token mechanism
- Password hashing with bcrypt

### Data Protection
- Input validation and sanitization
- SQL injection prevention with SQLAlchemy ORM
- Rate limiting on API endpoints
- CORS configuration for frontend

### Scraping Ethics
- Respect robots.txt files
- Implement delays between requests
- User-agent rotation
- Monitor for blocking and adjust accordingly

## Performance Optimization

### Database
- Connection pooling
- Query optimization with proper indexes
- Data archiving for old listings

### Scraping
- Parallel processing for multiple platforms
- Caching for repeated requests
- Error handling and retry logic

### Frontend
- Lazy loading for large datasets
- Chart virtualization for performance
- Caching API responses

## Monitoring & Logging

### Application Monitoring
- Health check endpoints
- Performance metrics (response times, error rates)
- Scraping success rates

### Logging
- Structured logging with JSON format
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Log rotation and retention policies

### Alerts
- Failed scraping sessions
- High error rates
- Database connection issues
- Authentication failures
