"""
Cars Trends Tool - Main Application Entry Point
Phase 0: Basic FastAPI setup
Phase 1: Craigslist scraper
Phase 2: Database storage
Phase 3: Frontend display
Phase 6: Mercado Libre scraper
Phase 8: Basic Analytics
Phase 16: Authentication
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from scrapers.craigslist import scrape_craigslist_tijuana
from scrapers.mercadolibre import scrape_mercadolibre_tijuana
from scrapers.facebook_marketplace import scrape_facebook_tijuana
from db_service import save_listing, get_all_listings, get_listings_by_platform, count_listings
from database import create_tables
from services.analytics_service import (
    get_top_cars, get_top_makes, get_market_summary,
    get_price_distribution, get_price_by_year, compare_platforms
)

app = FastAPI(
    title="Cars Trends API",
    description="API for tracking car market trends in Tijuana",
    version="0.3.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def startup_event():
    """Initialize database tables on app startup"""
    create_tables()


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Cars Trends API is running",
        "phase": "3 - Frontend Display"
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api_version": "0.1.0"
    }


@app.post("/scrape/craigslist")
def trigger_craigslist_scrape(max_results: int = 10, save_to_db: bool = True):
    """
    Manually trigger Craigslist scraper
    
    Args:
        max_results: Maximum number of listings to scrape (default: 10)
        save_to_db: Whether to save listings to database (default: True)
    
    Returns:
        List of scraped listings with title, price, url, and save status
    """
    listings = scrape_craigslist_tijuana(max_results=max_results)
    
    saved_count = 0
    duplicate_count = 0
    
    if save_to_db:
        for listing in listings:
            result = save_listing(
                platform="craigslist",
                title=listing["title"],
                url=listing["url"],
                price=listing.get("price"),
                make=listing.get("make"),
                model=listing.get("model"),
                year=listing.get("year"),
                mileage=listing.get("mileage")
            )
            if result:
                saved_count += 1
            else:
                duplicate_count += 1
    
    return {
        "success": True,
        "platform": "craigslist",
        "scraped": len(listings),
        "saved_to_db": saved_count,
        "duplicates_skipped": duplicate_count,
        "listings": listings
    }


@app.post("/scrape/mercadolibre")
def trigger_mercadolibre_scrape(max_results: int = 10, fetch_details: bool = True, save_to_db: bool = True):
    """
    Manually trigger Mercado Libre scraper
    
    Args:
        max_results: Maximum number of listings to scrape (default: 10)
        fetch_details: Whether to fetch detailed info from each listing page (default: True)
        save_to_db: Whether to save listings to database (default: True)
    
    Returns:
        List of scraped listings with title, price, url, and save status
    """
    listings = scrape_mercadolibre_tijuana(max_results=max_results, fetch_details=fetch_details)
    
    saved_count = 0
    duplicate_count = 0
    
    if save_to_db:
        for listing in listings:
            result = save_listing(
                platform="mercadolibre",
                title=listing["title"],
                url=listing["url"],
                price=listing.get("price"),
                make=listing.get("make"),
                model=listing.get("model"),
                year=listing.get("year"),
                mileage=listing.get("mileage"),
                views=listing.get("views")  # Phase 10: engagement metrics
            )
            if result:
                saved_count += 1
            else:
                duplicate_count += 1
    
    return {
        "success": True,
        "platform": "mercadolibre",
        "scraped": len(listings),
        "saved_to_db": saved_count,
        "duplicates_skipped": duplicate_count,
        "listings": listings
    }


@app.post("/scrape/facebook")
def trigger_facebook_scrape(max_results: int = 10, headless: bool = True, save_to_db: bool = True):
    """
    Manually trigger Facebook Marketplace scraper
    
    REQUIRES: fb_cookies.json file with Facebook authentication cookies
    See backend/HOW_TO_GET_FB_COOKIES.md for setup instructions
    
    Args:
        max_results: Maximum number of listings to scrape (default: 10)
        headless: Run browser in headless mode (default: True)
        save_to_db: Whether to save listings to database (default: True)
    
    Returns:
        Dict with scraping results including success status, scraped count, and listings
        
    Example response:
        {
            "success": True,
            "platform": "facebook",
            "scraped": 5,
            "saved_to_db": 5,
            "duplicates_skipped": 0,
            "listings": [...]
        }
    """
    try:
        listings = scrape_facebook_tijuana(max_results=max_results, headless=headless)
        
        saved_count = 0
        duplicate_count = 0
        
        if save_to_db:
            for listing in listings:
                result = save_listing(
                    platform="facebook",
                    title=listing["title"],
                    url=listing["url"],
                    price=listing.get("price"),
                    make=listing.get("make"),
                    model=listing.get("model"),
                    year=listing.get("year"),
                    mileage=listing.get("mileage"),
                    views=listing.get("views"),      # Phase 11: engagement metrics
                    likes=listing.get("likes"),      # Phase 11: engagement metrics
                    comments=listing.get("comments")  # Phase 11: engagement metrics
                )
                if result:
                    saved_count += 1
                else:
                    duplicate_count += 1
        
        return {
            "success": True,
            "platform": "facebook",
            "scraped": len(listings),
            "saved_to_db": saved_count,
            "duplicates_skipped": duplicate_count,
            "listings": listings
        }
        
    except Exception as e:
        return {
            "success": False,
            "platform": "facebook",
            "error": str(e),
            "message": "Facebook Marketplace scraping failed. Check that fb_cookies.json exists and is valid.",
            "scraped": 0,
            "saved_to_db": 0,
            "duplicates_skipped": 0,
            "listings": []
        }


@app.get("/listings")
def get_listings(platform: str = None, limit: int = 100):
    """
    Get all listings from database
    
    Args:
        platform: Optional platform filter ('craigslist', 'mercadolibre', 'facebook')
        limit: Maximum number of listings to return (default: 100)
    
    Returns:
        List of listings from database
    """
    if platform:
        listings = get_listings_by_platform(platform, limit=limit)
    else:
        listings = get_all_listings(limit=limit)
    
    # Convert to dict for JSON response (Phase 4: Added car fields, Phase 10: Added engagement)
    listings_data = [
        {
            "id": lst.id,
            "platform": lst.platform,
            "title": lst.title,
            "url": lst.url,
            "price": lst.price,
            "make": lst.make,
            "model": lst.model,
            "year": lst.year,
            "mileage": lst.mileage,
            "views": lst.views,  # Phase 10
            "likes": lst.likes,  # Phase 10
            "comments": lst.comments,  # Phase 10
            "scraped_at": lst.scraped_at.isoformat() if lst.scraped_at else None
        }
        for lst in listings
    ]
    
    return {
        "count": len(listings_data),
        "total_in_db": count_listings(),
        "listings": listings_data
    }


@app.get("/analytics/top-cars")
def analytics_top_cars(limit: int = 20, platform: str = None):
    """
    Get the most frequently listed cars
    
    Args:
        limit: Maximum number of results (default: 20)
        platform: Optional platform filter ('craigslist', 'mercadolibre')
        
    Returns:
        List of top cars with count and price statistics
    """
    top_cars = get_top_cars(limit=limit, platform=platform)
    return {
        "count": len(top_cars),
        "cars": top_cars
    }


@app.get("/analytics/top-makes")
def analytics_top_makes(limit: int = 10, platform: str = None):
    """
    Get the most frequently listed car brands
    
    Args:
        limit: Maximum number of results (default: 10)
        platform: Optional platform filter ('craigslist', 'mercadolibre')
        
    Returns:
        List of top makes with count, models count, and average price
    """
    top_makes = get_top_makes(limit=limit, platform=platform)
    return {
        "count": len(top_makes),
        "makes": top_makes
    }


@app.get("/analytics/summary")
def analytics_summary(platform: str = None):
    """
    Get overall market summary statistics
    
    Args:
        platform: Optional platform filter ('craigslist', 'mercadolibre')
        
    Returns:
        Market summary with total listings, unique makes/models, averages
    """
    summary = get_market_summary(platform=platform)
    return summary


@app.get("/analytics/prices/distribution")
def analytics_price_distribution(platform: str = None):
    """
    Get price distribution across different price ranges
    
    Args:
        platform: Optional platform filter ('craigslist', 'mercadolibre')
        
    Returns:
        Price distribution with ranges and counts
    """
    distribution = get_price_distribution(platform=platform)
    return distribution


@app.get("/analytics/prices/by-year")
def analytics_price_by_year(platform: str = None):
    """
    Get average price by vehicle year
    
    Args:
        platform: Optional platform filter ('craigslist', 'mercadolibre')
        
    Returns:
        List of years with average prices
    """
    price_by_year = get_price_by_year(platform=platform)
    return {
        "count": len(price_by_year),
        "data": price_by_year
    }


@app.get("/analytics/prices/compare-platforms")
def analytics_compare_platforms():
    """
    Compare pricing between Craigslist and Mercado Libre
    
    Returns:
        Platform comparison with price statistics
    """
    comparison = compare_platforms()
    return comparison


# ============================================================================
# TRENDS ENDPOINTS (Phase 13)
# ============================================================================

@app.get("/trends/price/{make}/{model}")
def get_price_trend_endpoint(make: str, model: str, days: int = 30):
    """
    Get price trend for a specific make/model over time
    
    Phase 13: Time Series - Price Trends
    
    Path Parameters:
        - make: Car make (e.g., 'Honda')
        - model: Car model (e.g., 'Civic')
    
    Query Parameters:
        - days: Number of days to look back (default: 30)
    
    Returns:
        List of daily snapshots with price history
        
    Example:
        GET /trends/price/Honda/Civic?days=7
        
        Response:
        [
            {
                "date": "2025-10-20",
                "avg_price": 18000.0,
                "listing_count": 12,
                "min_price": 15000.0,
                "max_price": 22000.0,
                "craigslist_count": 5,
                "mercadolibre_count": 4,
                "facebook_count": 3
            },
            ...
        ]
    """
    from services.trends_service import get_price_trend
    trend = get_price_trend(make, model, days)
    return trend


@app.get("/trends/trending")
def get_trending_cars_endpoint(days: int = 7, limit: int = 10):
    """
    Get cars with biggest price changes (trending up or down)
    
    Phase 13: Time Series - Price Trends
    
    Query Parameters:
        - days: Number of days to compare (default: 7)
        - limit: Maximum number of results (default: 10)
    
    Returns:
        List of cars sorted by price change magnitude
        
    Example:
        GET /trends/trending?days=7&limit=5
        
        Response:
        [
            {
                "make": "Honda",
                "model": "Civic",
                "old_price": 18000.0,
                "new_price": 19500.0,
                "change": 1500.0,
                "change_pct": 8.33,
                "direction": "up",
                "listing_count": 12
            },
            ...
        ]
    """
    from services.trends_service import get_trending_cars
    trending = get_trending_cars(days, limit)
    return trending


@app.get("/trends/overview")
def get_market_overview_endpoint(days: int = 30):
    """
    Get overview of market trends
    
    Phase 13: Time Series - Price Trends
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Returns:
        Market statistics and trends
        
    Example:
        GET /trends/overview?days=30
        
        Response:
        {
            "total_unique_cars": 45,
            "avg_market_price": 22500.0,
            "total_snapshots": 450,
            "date_range": {
                "start": "2025-09-26",
                "end": "2025-10-26"
            },
            "most_listed": [
                {
                    "make": "Honda",
                    "model": "Civic",
                    "avg_listings": 15.2,
                    "days_present": 28
                },
                ...
            ]
        }
    """
    from services.trends_service import get_market_overview
    overview = get_market_overview(days)
    return overview


@app.post("/trends/snapshot")
def create_snapshot_endpoint():
    """
    Manually trigger daily snapshot creation
    
    Phase 13: Time Series - Price Trends
    
    This endpoint creates/updates daily snapshots for all make/model combinations.
    Normally this would be called automatically on a schedule, but can also
    be triggered manually.
    
    Returns:
        Summary of snapshots created/updated
        
    Example:
        POST /trends/snapshot
        
        Response:
        {
            "date": "2025-10-26",
            "snapshots_created": 15,
            "snapshots_updated": 3,
            "total_cars": 18
        }
    """
    from services.trends_service import create_daily_snapshot
    result = create_daily_snapshot()
    return result


# ============================================================================
# SCHEDULER ENDPOINTS (Phase 14)
# ============================================================================

@app.get("/scheduler/status")
def get_scheduler_status_endpoint():
    """
    Get scheduler status and list of scheduled jobs
    
    Phase 14: Scheduling
    
    Returns:
        Scheduler status with job information
        
    Example:
        GET /scheduler/status
        
        Response:
        {
            "running": true,
            "message": "Scheduler is running",
            "jobs": [
                {
                    "id": "scrape_craigslist",
                    "name": "Scrape Craigslist Daily",
                    "next_run": "2025-10-27T02:00:00",
                    "trigger": "cron[hour='2', minute='0']"
                },
                ...
            ]
        }
    """
    from services.scheduler_service import get_scheduler_status
    return get_scheduler_status()


@app.post("/scheduler/start")
def start_scheduler_endpoint():
    """
    Start the scheduler
    
    Phase 14: Scheduling
    
    Starts the background scheduler which will run all scheduled jobs
    at their configured times. The scheduler runs these jobs:
    - Craigslist scraping: Daily at 2:00 AM
    - Mercado Libre scraping: Daily at 3:00 AM
    - Facebook scraping: Daily at 4:00 AM
    - Daily snapshot: Daily at 5:00 AM
    
    Returns:
        Status information
        
    Example:
        POST /scheduler/start
        
        Response:
        {
            "status": "started",
            "message": "Scheduler started successfully",
            "jobs": [...]
        }
    """
    from services.scheduler_service import start_scheduler
    return start_scheduler()


@app.post("/scheduler/stop")
def stop_scheduler_endpoint():
    """
    Stop the scheduler
    
    Phase 14: Scheduling
    
    Stops the background scheduler. Scheduled jobs will no longer run
    until the scheduler is started again.
    
    Returns:
        Status information
        
    Example:
        POST /scheduler/stop
        
        Response:
        {
            "status": "stopped",
            "message": "Scheduler stopped successfully"
        }
    """
    from services.scheduler_service import stop_scheduler
    return stop_scheduler()


@app.post("/scheduler/trigger/{job_id}")
def trigger_job_endpoint(job_id: str):
    """
    Manually trigger a specific job to run immediately
    
    Phase 14: Scheduling
    
    Path Parameters:
        - job_id: Job ID to trigger
    
    Valid job IDs:
        - scrape_craigslist
        - scrape_mercadolibre
        - scrape_facebook
        - daily_snapshot
    
    Returns:
        Job execution result
        
    Example:
        POST /scheduler/trigger/scrape_craigslist
        
        Response:
        {
            "success": true,
            "job_id": "scrape_craigslist",
            "result": "Craigslist: 15 saved, 3 duplicates"
        }
    """
    from services.scheduler_service import trigger_job_now
    return trigger_job_now(job_id)


# ============================================================================
# AUTHENTICATION ENDPOINTS (Phase 16)
# ============================================================================

def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract JWT token from Authorization header
    
    Args:
        authorization: Authorization header value
        
    Returns:
        JWT token string
        
    Raises:
        HTTPException: If token is missing or invalid format
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    return parts[1]


@app.post("/auth/register")
def register_endpoint(email: str, username: str, password: str):
    """
    Register a new user account
    
    Phase 16: Authentication
    
    Request Body (form data):
        - email: User's email address
        - username: Desired username
        - password: Password (will be hashed)
    
    Returns:
        User info and success message
        
    Example:
        POST /auth/register
        Content-Type: application/x-www-form-urlencoded
        email=user@example.com&username=john&password=secret123
        
        Response:
        {
            "message": "User registered successfully",
            "user": {
                "id": 1,
                "username": "john",
                "email": "user@example.com",
                "is_admin": false
            }
        }
    """
    from services.auth_service import register_user
    
    try:
        user = register_user(email, username, password)
        return {"message": "User registered successfully", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login")
def login_endpoint(username: str, password: str):
    """
    Login and receive JWT access token
    
    Phase 16: Authentication
    
    Request Body (form data):
        - username: Username or email
        - password: Password
    
    Returns:
        JWT access token and user info
        
    Example:
        POST /auth/login
        Content-Type: application/x-www-form-urlencoded
        username=john&password=secret123
        
        Response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "username": "john",
                "email": "user@example.com",
                "is_admin": false
            }
        }
    """
    from services.auth_service import login_user
    
    try:
        result = login_user(username, password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.get("/auth/me")
def get_current_user_endpoint(token: str = Depends(get_token_from_header)):
    """
    Get current user info from JWT token
    
    Phase 16: Authentication
    
    Headers:
        - Authorization: Bearer <token>
    
    Returns:
        Current user information
        
    Example:
        GET /auth/me
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        
        Response:
        {
            "id": 1,
            "username": "john",
            "email": "user@example.com",
            "is_admin": false,
            "is_active": true
        }
    """
    from services.auth_service import get_current_user
    
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user


@app.get("/auth/protected")
def protected_endpoint_example(token: str = Depends(get_token_from_header)):
    """
    Example of a protected endpoint that requires authentication
    
    Phase 16: Authentication
    
    Headers:
        - Authorization: Bearer <token>
    
    Returns:
        Success message with user info
        
    Example:
        GET /auth/protected
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
        
        Response:
        {
            "message": "This is a protected endpoint",
            "user": {...}
        }
    """
    from services.auth_service import get_current_user
    
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {
        "message": "This is a protected endpoint",
        "user": user
    }

