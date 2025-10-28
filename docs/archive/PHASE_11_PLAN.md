# Phase 11: Facebook Marketplace Scraper - Detailed Plan

**Overall Goal**: Add Facebook Marketplace as a third data source with engagement metrics

**Complexity Level**: 🔴 HIGH (authentication, JavaScript rendering, anti-bot measures)

**Strategy**: Build incrementally, test constantly, fail gracefully

---

## Sub-Phase 11.0: Research & Reconnaissance (15 min)
**Goal**: Understand FB Marketplace structure WITHOUT writing code

### Tasks:
- [ ] Manually visit FB Marketplace Tijuana car listings
- [ ] Document URL structure
- [ ] Identify data elements (title, price, location, engagement)
- [ ] Check if authentication is required for viewing
- [ ] Note any anti-bot measures observed

### Test:
- Document findings in a research file
- Identify 3-5 real listing URLs to use for testing

### Decision Point:
- ✅ If listings visible without auth → Proceed with simple scraper
- ❌ If auth required → Need Playwright approach
- ⚠️ If heavily protected → May need to defer this phase

**Time**: 15 minutes

---

## Sub-Phase 11.1: Basic FB Marketplace Scraper (No Auth) (45 min)
**Goal**: Create minimal scraper that tries to fetch listings without authentication

### Tasks:
- [ ] Create `backend/scrapers/facebook_marketplace.py`
- [ ] Implement `scrape_facebook_tijuana()` function
- [ ] Use requests + BeautifulSoup (same as other scrapers)
- [ ] Extract ONLY: title, price, url (no engagement yet)
- [ ] Handle errors gracefully

### Test:
```python
# Manual test
from scrapers.facebook_marketplace import scrape_facebook_tijuana
listings = scrape_facebook_tijuana(max_results=3)
print(f"Found {len(listings)} listings")
```

### Success Criteria:
- [ ] File created with proper structure
- [ ] Function returns list of dicts
- [ ] Can handle "access denied" gracefully
- [ ] Doesn't crash on errors

**Expected Outcome**: Likely will fail due to auth/JavaScript, but we'll learn what we're dealing with

**Time**: 45 minutes

---

## Sub-Phase 11.2: Playwright Setup (30 min)
**Goal**: Install and configure Playwright for JavaScript rendering

### Tasks:
- [ ] Add `playwright==1.40.0` to requirements.txt
- [ ] Install Playwright: `pip install playwright`
- [ ] Run: `playwright install chromium`
- [ ] Create simple test script to verify Playwright works
- [ ] Test loading any webpage with Playwright

### Test:
```python
# test_playwright.py
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.google.com')
    print(f"Title: {page.title()}")
    browser.close()
```

### Success Criteria:
- [ ] Playwright installed without errors
- [ ] Chromium browser downloaded
- [ ] Can load a webpage programmatically
- [ ] Test script runs successfully

**Time**: 30 minutes

---

## Sub-Phase 11.3: FB Login Strategy (RESEARCH ONLY) (20 min)
**Goal**: Determine authentication approach WITHOUT implementing

### Options to Research:
1. **Manual Cookie Export**: User logs in, exports cookies, we use them
2. **Playwright Auto-Login**: Automate login with Playwright
3. **Session Persistence**: Save session between scrapes

### Research Tasks:
- [ ] Check if FB Marketplace requires login for car listings
- [ ] Test if we can access listings with incognito/no-auth
- [ ] Document what data is visible without auth
- [ ] Identify login form elements (if needed)

### Decision Matrix:
| Approach | Pros | Cons | Feasibility |
|----------|------|------|-------------|
| No Auth (anonymous) | Simple, no credentials | Limited data, may block | Test first |
| Cookie Export | No automation risk | Manual process | High |
| Auto-Login | Fully automated | May trigger security | Medium |

### Deliverable:
- Decision document on which approach to use
- NO CODE WRITTEN in this sub-phase

**Time**: 20 minutes

---

## Sub-Phase 11.4A: Cookie-Based Authentication (IF NEEDED) (30 min)
**Goal**: Enable scraping with manually exported cookies

### Tasks:
- [ ] Create cookie storage mechanism
- [ ] Load cookies from JSON file
- [ ] Update scraper to use cookies
- [ ] Test with real FB cookies

### Test:
1. User manually logs into FB
2. Exports cookies (browser extension)
3. Saves to `backend/fb_cookies.json`
4. Scraper loads and uses cookies

### Success Criteria:
- [ ] Can load cookies from file
- [ ] Playwright uses cookies for requests
- [ ] Can access authenticated pages
- [ ] Graceful error if cookies expire

**Time**: 30 minutes

---

## Sub-Phase 11.4B: Anonymous Scraping (IF POSSIBLE) (30 min)
**Goal**: Extract data without authentication

### Tasks:
- [ ] Use Playwright to load FB Marketplace
- [ ] Extract visible listing data
- [ ] Handle "login prompt" if it appears
- [ ] Implement retry logic

### Test:
```python
from scrapers.facebook_marketplace import scrape_facebook_tijuana
listings = scrape_facebook_tijuana(max_results=5)
assert len(listings) > 0
assert 'title' in listings[0]
```

### Success Criteria:
- [ ] Can extract some listings without auth
- [ ] Handles rate limiting
- [ ] Returns valid data structure

**Time**: 30 minutes

---

## Sub-Phase 11.5: Data Extraction with Playwright (1 hour)
**Goal**: Extract title, price, URL from listings

### Tasks:
- [ ] Identify CSS selectors for listing elements
- [ ] Implement extraction logic
- [ ] Handle pagination (if applicable)
- [ ] Add proper delays to avoid detection

### Test:
```python
# Extract from single listing
listing = scraper._extract_listing_details(test_url)
assert listing['title'] is not None
assert listing['price'] is not None
assert listing['url'] is not None
```

### Success Criteria:
- [ ] Can extract title (car make/model/year)
- [ ] Can extract price
- [ ] Can extract listing URL
- [ ] Returns consistent data structure

**Time**: 1 hour

---

## Sub-Phase 11.6: Engagement Metrics Extraction (45 min)
**Goal**: Extract likes, comments, saves from FB listings

### Tasks:
- [ ] Identify engagement elements on listing pages
- [ ] Extract likes count
- [ ] Extract comments count
- [ ] Extract saves/shares (if visible)

### Test:
```python
listing = scraper._extract_engagement(test_url)
print(f"Likes: {listing['likes']}")
print(f"Comments: {listing['comments']}")
```

### Success Criteria:
- [ ] Can extract likes (or null if not visible)
- [ ] Can extract comments (or null if not visible)
- [ ] Gracefully handles missing data

**Time**: 45 minutes

---

## Sub-Phase 11.7: Car Details Parsing (30 min)
**Goal**: Extract car-specific fields (make, model, year, mileage)

### Tasks:
- [ ] Integrate with existing `parse_listing_title()`
- [ ] Extract from FB's structured fields (if available)
- [ ] Integrate with `normalize_car_data()`

### Test:
```python
listing = scrape_facebook_tijuana(max_results=1)[0]
assert listing['make'] is not None
assert listing['model'] is not None
assert listing['year'] is not None
```

### Success Criteria:
- [ ] Extracts car details
- [ ] Uses existing parser utilities
- [ ] Normalizes data consistently

**Time**: 30 minutes

---

## Sub-Phase 11.8: API Integration (30 min)
**Goal**: Add FB scraper endpoint to API

### Tasks:
- [ ] Add endpoint: `POST /scrape/facebook`
- [ ] Wire up to `save_listing()` with engagement metrics
- [ ] Test with real scraping
- [ ] Update frontend button

### Test:
```bash
curl -X POST "http://localhost:8000/scrape/facebook?max_results=5"
```

### Success Criteria:
- [ ] Endpoint exists
- [ ] Saves listings to database
- [ ] Returns proper response
- [ ] Engagement metrics saved

**Time**: 30 minutes

---

## Sub-Phase 11.9: Error Handling & Rate Limiting (30 min)
**Goal**: Handle FB's anti-bot measures gracefully

### Tasks:
- [ ] Add exponential backoff for rate limits
- [ ] Handle "Access Denied" errors
- [ ] Add user-agent rotation
- [ ] Implement request delays
- [ ] Log all errors properly

### Test:
- Trigger rate limit intentionally
- Verify scraper backs off and retries
- Check error logs are comprehensive

### Success Criteria:
- [ ] Doesn't crash on rate limit
- [ ] Backs off when blocked
- [ ] Logs errors clearly
- [ ] Returns partial results if some fail

**Time**: 30 minutes

---

## Sub-Phase 11.10: Testing & Validation (45 min)
**Goal**: Comprehensive tests for FB scraper

### Tasks:
- [ ] Create `tests/test_facebook.py`
- [ ] Test scraper structure
- [ ] Test data extraction
- [ ] Test error handling
- [ ] Test engagement metrics
- [ ] Integration test with real data

### Success Criteria:
- [ ] All tests pass
- [ ] Test coverage > 80%
- [ ] Real scraping works end-to-end

**Time**: 45 minutes

---

## Decision Points & Pivots

### If FB blocks aggressively:
- ✅ **Pivot**: Implement "manual import" feature
  - User manually downloads FB data
  - We provide import endpoint
  - Still get engagement metrics

### If authentication too complex:
- ✅ **Pivot**: Use cookie-based approach
  - User provides cookies once
  - We refresh periodically

### If Playwright too heavy:
- ✅ **Pivot**: Use Selenium as alternative
  - Similar functionality
  - May be lighter weight

---

## Total Time Estimate: 5-6 hours
(Broken into 10 sub-phases of 15-60 minutes each)

## Testing Strategy
- ✅ Test after EACH sub-phase
- ✅ Manual verification before automation
- ✅ Keep test URLs handy
- ✅ Document what works and what doesn't
- ✅ Be ready to pivot if blocked

## Success Metrics
- [ ] Can scrape at least 5 listings
- [ ] Engagement metrics captured
- [ ] 50%+ success rate
- [ ] No crashes on errors
- [ ] All existing tests still pass

