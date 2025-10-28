# Cars Trends Tool - Incremental Build Plan

## 🎯 Project Goal
Build a web application that scrapes car listings from Facebook Marketplace, Craigslist, and Mercado Libre (Tijuana area), tracks engagement metrics, and displays market trends through an analytics dashboard.

## 🏗️ Build Philosophy
1. **Minimal viable increments** - Each phase builds ONE small feature
2. **Test-driven** - Write tests first, then implement
3. **Validate before moving** - Each phase must work completely before proceeding
4. **No big-bang** - Avoid building multiple components simultaneously
5. **Real data early** - Start scraping real data as soon as possible

---

## Phase 0: Clean Slate Setup (Day 1)
**Goal**: Start completely fresh with minimal project structure

### Tasks
- [ ] Delete all existing code (keep docs for reference)
- [ ] Create new minimal project structure
- [ ] Set up Python virtual environment
- [ ] Install minimal dependencies
- [ ] Create `.gitignore`

### Directory Structure
```
cars-trends-tool/
├── backend/
│   ├── main.py                 # Entry point
│   ├── requirements.txt        # Minimal deps
│   └── tests/
│       └── test_basic.py       # Sanity test
├── .gitignore
└── INCREMENTAL_BUILD_PLAN.md
```

### Minimal Dependencies
```
pytest==7.4.3
fastapi==0.104.1
uvicorn==0.24.0
```

### Success Criteria
- ✅ Virtual environment created and activated
- ✅ Can run `pytest` successfully
- ✅ FastAPI app starts with `uvicorn main:app`
- ✅ Can access http://localhost:8000 with a simple "Hello World" endpoint

### Tests
```python
# tests/test_basic.py
def test_imports():
    """Verify core libraries are importable"""
    import fastapi
    import pytest
    assert True

def test_app_exists():
    """Verify FastAPI app exists"""
    from main import app
    assert app is not None
```

**Time Estimate**: 30 minutes

---

## Phase 1: Simple Craigslist Scraper (Day 1-2)
**Goal**: Build ONE working scraper with real data (start with easiest platform)

### Why Craigslist First?
- Simplest HTML structure (no authentication required)
- Static content (no JavaScript rendering needed)
- Good for learning the patterns

### Tasks
- [ ] Install scraping dependencies (requests, beautifulsoup4)
- [ ] Create `scrapers/craigslist.py`
- [ ] Implement basic Craigslist search for Tijuana cars
- [ ] Extract: title, price, url
- [ ] Write tests for scraper
- [ ] Verify scraper gets real listings

### Dependencies Added
```
requests==2.31.0
beautifulsoup4==4.12.2
```

### Implementation
```python
# scrapers/craigslist.py
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

def scrape_craigslist_tijuana(max_results: int = 10) -> List[Dict]:
    """
    Scrape car listings from Craigslist Tijuana
    Returns list of dicts with: title, price, url
    """
    pass  # Implement in this phase
```

### Success Criteria
- ✅ Scraper runs without errors
- ✅ Returns list of at least 5 real listings
- ✅ Each listing has title, price, url
- ✅ All tests pass
- ✅ Can run manually: `python -m scrapers.craigslist`

### Tests
```python
# tests/test_craigslist.py
def test_craigslist_scraper_returns_data():
    from scrapers.craigslist import scrape_craigslist_tijuana
    listings = scrape_craigslist_tijuana(max_results=5)
    assert len(listings) > 0
    assert 'title' in listings[0]
    assert 'price' in listings[0]
    assert 'url' in listings[0]

def test_craigslist_scraper_respects_limit():
    from scrapers.craigslist import scrape_craigslist_tijuana
    listings = scrape_craigslist_tijuana(max_results=3)
    assert len(listings) <= 3
```

**Time Estimate**: 2-3 hours

---

## Phase 2: Data Storage - SQLite (Day 2)
**Goal**: Store scraped listings in a simple database

### Why SQLite First?
- No setup required (file-based)
- Easy to inspect data
- Can upgrade to PostgreSQL later

### Tasks
- [ ] Install SQLAlchemy
- [ ] Create simple `Listing` model (id, platform, title, price, url, scraped_at)
- [ ] Create database initialization
- [ ] Update scraper to save to DB
- [ ] Write tests

### Dependencies Added
```
sqlalchemy==2.0.23
```

### Implementation
```python
# models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Listing(Base):
    __tablename__ = 'listings'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(20), nullable=False)
    title = Column(String(500), nullable=False)
    price = Column(Float)
    url = Column(String(1000), nullable=False, unique=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
```

### Success Criteria
- ✅ Database file created (`listings.db`)
- ✅ Scraper saves listings to database
- ✅ Can query listings from database
- ✅ No duplicate URLs stored
- ✅ All tests pass

### Tests
```python
# tests/test_database.py
def test_listing_model_creation():
    from models import Listing, engine, Base
    Base.metadata.create_all(engine)
    # Create test listing
    # Verify it's saved

def test_no_duplicate_urls():
    # Try to save same listing twice
    # Verify only one exists
```

**Time Estimate**: 2 hours

---

## Phase 3: Simple API Endpoint (Day 3)
**Goal**: Expose listings through a REST API

### Tasks
- [ ] Create GET `/listings` endpoint
- [ ] Return JSON list of all listings
- [ ] Add query parameter for platform filter
- [ ] Write API tests
- [ ] Test with browser/curl

### Implementation
```python
# main.py
from fastapi import FastAPI
from sqlalchemy.orm import Session
from models import Listing, SessionLocal
from typing import List, Optional

app = FastAPI(title="Cars Trends API")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/listings")
def get_listings(platform: Optional[str] = None, limit: int = 50):
    """Get listings, optionally filtered by platform"""
    pass  # Implement

@app.post("/scrape/craigslist")
def trigger_craigslist_scrape():
    """Manually trigger Craigslist scrape"""
    pass  # Implement
```

### Success Criteria
- ✅ Can access http://localhost:8000/listings
- ✅ Returns JSON with all listings
- ✅ Filter works: `/listings?platform=craigslist`
- ✅ Manual scrape trigger works: POST `/scrape/craigslist`
- ✅ All tests pass

### Tests
```python
# tests/test_api.py
from fastapi.testclient import TestClient

def test_listings_endpoint():
    client = TestClient(app)
    response = client.get("/listings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_scrape_trigger():
    client = TestClient(app)
    response = client.post("/scrape/craigslist")
    assert response.status_code == 200
```

**Time Estimate**: 2 hours

---

## Phase 4: Basic Frontend Display (Day 3-4)
**Goal**: Display listings in a simple HTML page

### Why Plain HTML First?
- No build process complexity
- Fast to iterate
- Can upgrade to React later

### Tasks
- [ ] Create `frontend/index.html`
- [ ] Add simple JavaScript to fetch from API
- [ ] Display listings in a table
- [ ] Add CORS to backend
- [ ] Test in browser

### Implementation
```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Cars Trends - Listings</title>
    <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>Car Listings</h1>
    <button onclick="fetchListings()">Refresh</button>
    <table id="listingsTable">
        <thead>
            <tr><th>Platform</th><th>Title</th><th>Price</th><th>Link</th></tr>
        </thead>
        <tbody id="listingsBody"></tbody>
    </table>
    <script>
        async function fetchListings() {
            const response = await fetch('http://localhost:8000/listings');
            const listings = await response.json();
            // Populate table
        }
        fetchListings();
    </script>
</body>
</html>
```

### Dependencies Added (Backend)
```
python-multipart==0.0.6  # For CORS
```

### Success Criteria
- ✅ Open `index.html` in browser
- ✅ See listings displayed in table
- ✅ Refresh button works
- ✅ Links are clickable
- ✅ No CORS errors in console

**Time Estimate**: 2 hours

---

## Phase 5: Enhanced Craigslist Scraper (Day 4)
**Goal**: Extract more fields from Craigslist listings

### Tasks
- [ ] Add extraction for: make, model, year, mileage, location
- [ ] Update database model
- [ ] Create data migration (add columns)
- [ ] Update frontend to show new fields
- [ ] Write tests

### Enhanced Model
```python
# models.py - updated
class Listing(Base):
    # ... existing fields ...
    make = Column(String(50))
    model = Column(String(50))
    year = Column(Integer)
    mileage = Column(Integer)
    location = Column(String(100))
```

### Success Criteria
- ✅ Scraper extracts make/model/year when available
- ✅ Database stores new fields
- ✅ Frontend displays new fields
- ✅ Handles missing data gracefully
- ✅ All tests pass

**Time Estimate**: 3 hours

---

## Phase 6: Second Scraper - Mercado Libre (Day 5-6)
**Goal**: Add second data source

### Why Mercado Libre Second?
- Similar to Craigslist (static-ish content)
- Huge platform in Mexico
- Good test of multi-platform approach

### Tasks
- [ ] Research Mercado Libre HTML structure
- [ ] Create `scrapers/mercadolibre.py`
- [ ] Implement scraper (title, price, url, make, model, year)
- [ ] Add to API: POST `/scrape/mercadolibre`
- [ ] Test with real data
- [ ] Write tests

### Success Criteria
- ✅ Mercado Libre scraper returns listings
- ✅ Listings stored in same database
- ✅ Can see both platforms in frontend
- ✅ Platform filter works for both
- ✅ All tests pass

**Time Estimate**: 3-4 hours

---

## Phase 7: Data Normalization (Day 6-7)
**Goal**: Clean and standardize car make/model names

### The Problem
- "Honda Accord" vs "HONDA ACCORD" vs "honda accord"
- "Toyota Camry" vs "Camry Toyota"
- "BMW 3-Series" vs "BMW 3 Series" vs "BMW 3-series"

### Tasks
- [ ] Create `utils/normalizer.py`
- [ ] Build make/model mapping dictionary
- [ ] Implement normalization function
- [ ] Apply to scrapers before saving
- [ ] Write tests
- [ ] Run migration on existing data

### Implementation
```python
# utils/normalizer.py
def normalize_car_data(title: str, make: str = None, model: str = None) -> dict:
    """
    Normalize car make/model from title and fields
    Returns: {'make': 'Honda', 'model': 'Accord'}
    """
    pass  # Implement with common patterns
```

### Success Criteria
- ✅ Normalizer handles common variations
- ✅ Database has cleaner make/model data
- ✅ Similar cars are grouped together
- ✅ All tests pass

**Time Estimate**: 3 hours

---

## Phase 8: Basic Analytics - Top Cars (Day 7-8)
**Goal**: Show which cars appear most frequently

### Tasks
- [ ] Create analytics service
- [ ] Add endpoint: GET `/analytics/top-cars`
- [ ] Count listings by make/model
- [ ] Display in frontend as list
- [ ] Write tests

### Implementation
```python
# main.py
@app.get("/analytics/top-cars")
def get_top_cars(limit: int = 20):
    """Get most frequently listed cars"""
    # Query DB, group by make/model, count, order by count desc
    pass
```

### Success Criteria
- ✅ API returns top 20 cars by listing count
- ✅ Frontend displays top cars list
- ✅ Numbers are accurate
- ✅ All tests pass

**Time Estimate**: 2 hours

---

## Phase 9: Price Analytics (Day 8-9)
**Goal**: Show average prices by make/model

### Tasks
- [ ] Add endpoint: GET `/analytics/avg-prices`
- [ ] Calculate average, min, max prices per car
- [ ] Display in frontend
- [ ] Handle missing/invalid prices
- [ ] Write tests

### Success Criteria
- ✅ API returns price statistics
- ✅ Frontend shows avg/min/max prices
- ✅ Invalid prices filtered out
- ✅ All tests pass

**Time Estimate**: 2 hours

---

## Phase 10: Engagement Metrics Scraping (Day 9-11)
**Goal**: Extract views, likes, comments from listings

### Challenge
This is harder because:
- Facebook Marketplace requires authentication
- Dynamic content (JavaScript rendering)
- Rate limiting concerns

### Approach
1. Start with Mercado Libre (easier than Facebook)
2. Use Playwright for JavaScript rendering
3. Add engagement fields to model

### Tasks
- [ ] Install Playwright
- [ ] Create engagement scraper for Mercado Libre
- [ ] Add engagement columns to database
- [ ] Test extraction
- [ ] Write tests

### Dependencies Added
```
playwright==1.40.0
```

### Success Criteria
- ✅ Scraper extracts views, likes (where available)
- ✅ Database stores engagement data
- ✅ Frontend displays engagement metrics
- ✅ All tests pass

**Time Estimate**: 4-5 hours

---

## Phase 11: Facebook Marketplace Scraper (Day 11-13)
**Goal**: Add the most complex scraper

### Challenge
- Requires authentication
- Heavy JavaScript
- Anti-bot measures

### Tasks
- [ ] Research FB Marketplace structure
- [ ] Set up Playwright with authentication
- [ ] Create scraper (careful with rate limits)
- [ ] Test thoroughly
- [ ] Write tests
- [ ] Add error handling

### Success Criteria
- ✅ Scraper works reliably (at least 50% success rate)
- ✅ Extracts basic fields + engagement
- ✅ Doesn't get blocked immediately
- ✅ All tests pass
- ✅ Good error logging

**Time Estimate**: 6-8 hours (most complex phase)

---

## Phase 12: Engagement Analytics (Day 13-14)
**Goal**: Show top cars by engagement, not just listing count

### Tasks
- [ ] Create engagement scoring algorithm
- [ ] Add endpoint: GET `/analytics/top-by-engagement`
- [ ] Calculate engagement score (views + likes*2 + comments*3)
- [ ] Display in frontend
- [ ] Write tests

### Success Criteria
- ✅ Engagement score calculated correctly
- ✅ Can sort cars by engagement
- ✅ Frontend shows engagement leaders
- ✅ All tests pass

**Time Estimate**: 2 hours

---

## Phase 13: Time Series - Price Trends (Day 14-15)
**Goal**: Track how prices change over time

### Tasks
- [ ] Create daily snapshot job
- [ ] Add trends table (date, make, model, avg_price, listing_count)
- [ ] Add endpoint: GET `/trends/price/{make}/{model}`
- [ ] Simple line chart in frontend
- [ ] Write tests

### Implementation
```python
# models.py
class DailySnapshot(Base):
    __tablename__ = 'daily_snapshots'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    make = Column(String(50))
    model = Column(String(50))
    avg_price = Column(Float)
    listing_count = Column(Integer)
    total_views = Column(Integer)
    total_likes = Column(Integer)
```

### Success Criteria
- ✅ Daily snapshots created automatically
- ✅ Can query historical trends
- ✅ Frontend shows price trend chart
- ✅ All tests pass

**Time Estimate**: 3-4 hours

---

## Phase 14: Scheduling (Day 15-16)
**Goal**: Automate daily scraping

### Tasks
- [ ] Install APScheduler
- [ ] Create scheduler service
- [ ] Schedule all scrapers to run daily
- [ ] Add logging
- [ ] Create scraping history tracking
- [ ] Write tests

### Dependencies Added
```
apscheduler==3.10.4
```

### Success Criteria
- ✅ Scrapers run automatically at scheduled time
- ✅ Errors are logged
- ✅ Can see scraping history
- ✅ Can disable/enable schedulers
- ✅ All tests pass

**Time Estimate**: 3 hours

---

## Phase 15: Better Frontend (Day 16-18)
**Goal**: Upgrade to React with proper UI

### Tasks
- [ ] Set up React + TypeScript
- [ ] Create components (Dashboard, ListingsTable, TrendsChart)
- [ ] Use Chart.js for visualizations
- [ ] Add Tailwind CSS
- [ ] Migrate all features from HTML version
- [ ] Test in browser

### Success Criteria
- ✅ React app builds and runs
- ✅ All features from HTML version work
- ✅ Charts display correctly
- ✅ Responsive design
- ✅ No console errors

**Time Estimate**: 6-8 hours

---

## Phase 16: Authentication (Day 18-19)
**Goal**: Add user login

### Tasks
- [ ] Create User model
- [ ] Add JWT authentication
- [ ] Create login endpoint
- [ ] Add auth middleware
- [ ] Protected routes
- [ ] Login page in frontend
- [ ] Write tests

### Success Criteria
- ✅ User can register and login
- ✅ JWT tokens work
- ✅ Protected endpoints require auth
- ✅ Frontend handles auth state
- ✅ All tests pass

**Time Estimate**: 4-5 hours

---

## Phase 17: PostgreSQL Migration (Day 19-20)
**Goal**: Upgrade from SQLite to PostgreSQL

### Why Wait Until Now?
- SQLite is sufficient for development
- PostgreSQL adds deployment complexity
- Better to switch when data model is stable

### Tasks
- [ ] Install PostgreSQL
- [ ] Update connection string
- [ ] Create migration scripts
- [ ] Test all features still work
- [ ] Update tests

### Success Criteria
- ✅ App runs on PostgreSQL
- ✅ All data migrated
- ✅ All features still work
- ✅ All tests pass

**Time Estimate**: 2-3 hours

---

## Phase 18: Docker Deployment (Day 20-21)
**Goal**: Containerize everything

### Tasks
- [ ] Create backend Dockerfile
- [ ] Create frontend Dockerfile  
- [ ] Create docker-compose.yml
- [ ] Test full stack deployment
- [ ] Add environment variables
- [ ] Document deployment

### Success Criteria
- ✅ `docker-compose up` starts everything
- ✅ Backend, frontend, database all running
- ✅ Can access application
- ✅ All features work
- ✅ Data persists across restarts

**Time Estimate**: 3-4 hours

---

## Phase 19: Production Hardening (Day 21-22)
**Goal**: Make it production-ready

### Tasks
- [ ] Add proper error handling
- [ ] Improve logging
- [ ] Add health check endpoints
- [ ] Set up monitoring
- [ ] Add rate limiting
- [ ] Security review
- [ ] Performance optimization
- [ ] Write deployment docs

### Success Criteria
- ✅ Proper error messages
- ✅ Structured logging
- ✅ Health checks work
- ✅ Rate limiting active
- ✅ Security best practices followed

**Time Estimate**: 4-5 hours

---

## Phase 20: Testing & Bug Fixes (Day 22-23)
**Goal**: Ensure everything works together

### Tasks
- [ ] End-to-end testing
- [ ] Load testing
- [ ] Bug fixes
- [ ] Documentation updates
- [ ] User acceptance testing

### Success Criteria
- ✅ All tests pass
- ✅ No critical bugs
- ✅ Documentation complete
- ✅ Ready for real use

**Time Estimate**: 4-6 hours

---

## 📊 Summary

**Total Estimated Time**: 20-23 days of focused work

**Total Phases**: 20 phases

**Key Milestones**:
- Day 2: First scraper working
- Day 4: Basic frontend showing data
- Day 6: Multiple platforms scraping
- Day 11: Engagement metrics working
- Day 15: Time series and trends
- Day 18: React frontend complete
- Day 21: Docker deployment ready
- Day 23: Production ready

---

## 🎯 Critical Success Factors

1. **Don't skip ahead** - Finish each phase completely
2. **Test everything** - Every phase has tests
3. **Commit frequently** - Commit after each working phase
4. **Real data early** - Start with actual scraping ASAP
5. **Simple first** - Start with easiest platforms/features
6. **Validate often** - Manual testing + automated tests
7. **Document issues** - Keep a log of problems encountered
8. **Stay focused** - One feature at a time

---

## 🚨 Red Flags to Watch For

- **Scope creep** - Building features not in current phase
- **Skipping tests** - "I'll test it later"
- **Complexity explosion** - Adding too many abstractions
- **Perfect syndrome** - Over-engineering simple solutions
- **Integration hell** - Building too much before integrating

---

## 📝 Daily Checklist

At end of each phase:
- [ ] All tests pass
- [ ] Feature works manually
- [ ] Code committed
- [ ] Documentation updated
- [ ] Next phase planned

---

## 🎓 Lessons from Previous Attempt

What went wrong before:
1. Built too much at once
2. Didn't test incrementally
3. Complex abstractions too early
4. Tried to finish everything before testing anything

What we'll do differently:
1. Build one tiny piece at a time
2. Test after every change
3. Start simple, refactor later
4. Get real data flowing immediately

---

## Ready to Start?

Say the word and we'll begin with **Phase 0: Clean Slate Setup**!

