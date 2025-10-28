# Phase 19.6: Automatic Scheduling & Data Seeding - Design Document

## 🎯 Goals

1. **Automatic Daily Scraping**: Scheduler runs automatically, not user-controlled
2. **Pre-populated Database**: Initial data seeding for immediate value

## 📋 Current vs Desired State

### Current State ❌
- Scheduler has manual start/stop endpoints
- Empty database on first deployment
- Users control when scraping happens
- No initial data = no trends to show

### Desired State ✅
- Scheduler auto-starts on application launch
- Database pre-populated with real data
- Scraping happens automatically daily at set times
- New deployments have immediate value
- Admin-only controls (if needed)

## 🎨 Design Overview

```
┌─────────────────────────────────────────┐
│     Application Startup                 │
├─────────────────────────────────────────┤
│  1. Initialize Database                 │
│  2. Check if data exists                │
│  3. If empty → Run initial seed         │
│  4. Auto-start scheduler                │
│  5. Schedule daily jobs:                │
│     - 2 AM: Scrape Craigslist          │
│     - 3 AM: Scrape Mercado Libre       │
│     - 4 AM: Scrape Facebook            │
│     - 5 AM: Create daily snapshot      │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│     Daily Operations                    │
├─────────────────────────────────────────┤
│  • Automatic scraping (no user action) │
│  • Continuous data collection           │
│  • All users see same live data         │
│  • Trends updated daily                 │
└─────────────────────────────────────────┘
```

## 📦 Components to Modify/Create

### 1. Scheduler Service (`services/scheduler_service.py`)
**Changes**:
- Remove manual start/stop (keep for admin only)
- Auto-initialize on import
- Auto-start on application startup
- Add startup check to prevent duplicate schedulers

**New Functions**:
- `auto_initialize_scheduler()` - Called on app startup
- `is_scheduler_running()` - Check if already running
- `get_scheduler_instance()` - Singleton pattern

### 2. Main Application (`main.py`)
**Changes**:
- Add startup event to auto-initialize scheduler
- Remove scheduler control endpoints (or make admin-only)
- Add health check endpoint to verify scheduler status

**New Startup Sequence**:
```python
@app.on_event("startup")
async def startup_event():
    # 1. Create database tables
    create_tables()
    
    # 2. Seed data if empty
    await seed_initial_data()
    
    # 3. Auto-start scheduler
    auto_initialize_scheduler()
```

### 3. Data Seeding Script (`seed_data.py`)
**New File**:
- Check if database has data
- If empty, run initial scraping
- Run all three scrapers sequentially
- Create initial daily snapshot
- Log results

**Features**:
- Idempotent (safe to run multiple times)
- Skip if data already exists
- Progress logging
- Error handling
- Can be run manually: `python seed_data.py`

### 4. Frontend Updates (`frontend/index.html`)
**Changes**:
- Remove scheduler control UI (start/stop buttons)
- Add "Last Updated" timestamp
- Show scheduler status (read-only)
- Indicate data freshness

### 5. Documentation Updates
**Files to Update**:
- `README.md` - Mention automatic scheduling
- `DOCKER_DEPLOYMENT.md` - Note auto-start behavior
- `docs/user_guide.md` - Explain data refresh schedule

## 🔧 Implementation Plan

### Task 1: Create Data Seeding Script (30 min)

**File**: `backend/seed_data.py`

**Purpose**: Pre-populate database with initial data

**Features**:
- Check if listings exist
- Run all three scrapers if empty
- Create initial snapshot
- Can run standalone or on startup

**Usage**:
```bash
# Manual run
cd backend
python seed_data.py

# Or Docker
docker-compose exec backend python seed_data.py
```

**Logic**:
```python
def seed_initial_data():
    # 1. Check if database has listings
    listing_count = count_listings()
    
    if listing_count > 0:
        print(f"Database already has {listing_count} listings. Skipping seed.")
        return
    
    print("Database empty. Running initial scraping...")
    
    # 2. Run scrapers
    scrape_craigslist_tijuana()
    scrape_mercadolibre_tijuana()
    scrape_facebook_tijuana()
    
    # 3. Create initial snapshot
    create_daily_snapshot()
    
    print("Initial data seeding complete!")
```

### Task 2: Modify Scheduler Service (30 min)

**File**: `backend/services/scheduler_service.py`

**Changes**:

1. **Auto-initialize on startup**:
```python
def auto_initialize_scheduler():
    """Auto-initialize and start scheduler on application startup"""
    global _scheduler
    
    if _scheduler is not None and _scheduler.running:
        logger.info("Scheduler already running")
        return _scheduler
    
    logger.info("Auto-initializing scheduler...")
    initialize_scheduler()
    start_scheduler()
    logger.info("Scheduler auto-started successfully")
    
    return _scheduler
```

2. **Add safety checks**:
```python
def is_scheduler_running():
    """Check if scheduler is currently running"""
    return _scheduler is not None and _scheduler.running
```

3. **Keep admin endpoints** (optional):
- Keep status endpoint (GET /scheduler/status) - read-only
- Move start/stop to admin-only routes
- Or remove entirely for simplicity

### Task 3: Update Main Application (20 min)

**File**: `backend/main.py`

**Changes**:

1. **Add startup event**:
```python
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("=== Application Startup ===")
    
    # 1. Create database tables
    logger.info("Creating database tables...")
    create_tables()
    
    # 2. Seed initial data if needed
    logger.info("Checking for initial data...")
    from seed_data import seed_initial_data
    seed_initial_data()
    
    # 3. Auto-start scheduler
    logger.info("Starting scheduler...")
    from services.scheduler_service import auto_initialize_scheduler
    auto_initialize_scheduler()
    
    logger.info("=== Startup Complete ===")
```

2. **Update scheduler endpoints**:
   - **Option A** (Simplest): Remove all scheduler control endpoints
   - **Option B** (Admin): Keep but require authentication
   - **Option C** (Read-only): Keep status, remove start/stop

**Recommendation**: Option A (remove controls) for public deployment

3. **Add health check**:
```python
@app.get("/health")
def health_check():
    """Health check endpoint with scheduler status"""
    from services.scheduler_service import get_scheduler_status
    
    status = get_scheduler_status()
    
    return {
        "status": "healthy",
        "scheduler_running": status["running"],
        "jobs_count": len(status["jobs"]),
        "database": "connected"
    }
```

### Task 4: Update Frontend (15 min)

**File**: `frontend/index.html`

**Remove**:
- Scheduler control bar (start/stop/refresh buttons)
- `loadSchedulerStatus()` function
- `startScheduler()` function
- `stopScheduler()` function

**Add**:
- "Data last updated: [timestamp]" display
- Pull from listings API to show most recent scrape time
- Make it read-only information

**Example**:
```html
<div class="info-bar">
    <span>📊 Market data automatically updated daily</span>
    <span id="lastUpdate">Last update: Loading...</span>
</div>
```

```javascript
async function loadLastUpdateTime() {
    const response = await fetch(`${API_BASE_URL}/analytics/summary`);
    const data = await response.json();
    
    if (data.most_recent_listing) {
        const timestamp = new Date(data.most_recent_listing);
        document.getElementById('lastUpdate').textContent = 
            `Last update: ${timestamp.toLocaleString()}`;
    }
}
```

### Task 5: Update Documentation (10 min)

**Files to Update**:

1. **README.md**:
```markdown
## Automated Data Collection

The application automatically scrapes car listings daily:
- **2 AM**: Craigslist Tijuana
- **3 AM**: Mercado Libre Tijuana  
- **4 AM**: Facebook Marketplace Tijuana
- **5 AM**: Create daily market snapshot

No manual intervention required - data is always fresh!
```

2. **DOCKER_DEPLOYMENT.md**:
```markdown
## Automatic Scheduling

The scheduler starts automatically when the application launches.
On first deployment, the database is pre-populated with initial data.

Daily scraping schedule:
- All times in America/Tijuana timezone
- Scraping happens automatically
- No user action required
```

### Task 6: Test Everything (20 min)

**Test Checklist**:
- [ ] Start fresh container → database seeds automatically
- [ ] Scheduler starts automatically
- [ ] Jobs are scheduled correctly
- [ ] First scraping runs successfully
- [ ] Daily snapshot created
- [ ] Frontend shows data immediately
- [ ] No manual intervention needed
- [ ] Restart container → scheduler resumes
- [ ] No duplicate schedulers created

## 🎯 Success Criteria

### Must Have ✅
- [ ] Scheduler auto-starts on application launch
- [ ] Database seeds with initial data on first run
- [ ] Daily scraping runs automatically (no user control)
- [ ] All three scrapers run on schedule
- [ ] Daily snapshots created automatically
- [ ] Frontend shows data immediately on fresh deploy
- [ ] No manual scheduler control needed
- [ ] Documentation updated

### Nice to Have 🎯
- [ ] Admin-only scheduler controls (optional)
- [ ] Scheduler status visible to users (read-only)
- [ ] Email notifications on scrape completion (future)
- [ ] Configurable schedule via environment variables

## 📊 Testing Strategy

### Test 1: Fresh Deployment
```bash
# 1. Delete existing database
rm backend/listings.db

# 2. Start application
cd backend
python main.py

# Expected:
# - Database created
# - Initial data seeding runs
# - Scheduler starts automatically
# - Jobs scheduled
```

### Test 2: Existing Data
```bash
# 1. Start with existing database
cd backend
python main.py

# Expected:
# - Database checked
# - Seeding skipped (data exists)
# - Scheduler starts
# - No duplicate data
```

### Test 3: Manual Seeding
```bash
# Test standalone seeding script
cd backend
python seed_data.py

# Expected:
# - Checks for existing data
# - Runs or skips appropriately
# - Logs progress
```

### Test 4: Docker Deployment
```bash
# Fresh Docker deployment
docker-compose down -v  # Remove volumes
docker-compose up -d

# Expected:
# - Container starts
# - Database initialized
# - Data seeded
# - Scheduler running
# - API accessible with data
```

## 🚨 Potential Issues & Solutions

### Issue 1: Slow Initial Seeding
**Problem**: First deployment takes 5-10 minutes for scraping
**Solution**: 
- Show loading message in UI
- Run seeding in background thread
- Add progress endpoint: `GET /seeding/status`

### Issue 2: Scheduler Doesn't Start
**Problem**: Scheduler fails to initialize
**Solution**:
- Add comprehensive logging
- Check for port conflicts
- Verify timezone configuration
- Add retry logic

### Issue 3: Duplicate Schedulers
**Problem**: Multiple scheduler instances created
**Solution**:
- Use singleton pattern
- Check `_scheduler.running` before starting
- Add process lock file

### Issue 4: Data Already Exists
**Problem**: Seeding tries to add duplicate data
**Solution**:
- Check listing count before seeding
- Use idempotent operations
- Skip if data exists
- Log skip reason

### Issue 5: Facebook Cookies Not Available
**Problem**: Facebook scraping fails during seeding
**Solution**:
- Make Facebook scraping optional during seed
- Provide clear error message
- Document cookie setup requirement
- Seed with Craigslist + Mercado Libre only

## 📝 Implementation Sequence

### Phase 1: Core Changes (45 min)
1. Create `seed_data.py` script
2. Modify `scheduler_service.py` for auto-start
3. Update `main.py` startup event
4. Test locally

### Phase 2: Frontend Updates (15 min)
5. Remove scheduler controls from UI
6. Add read-only data freshness display
7. Test UI changes

### Phase 3: Documentation (10 min)
8. Update README.md
9. Update DOCKER_DEPLOYMENT.md
10. Update user guide

### Phase 4: Testing & Validation (20 min)
11. Test fresh deployment
12. Test existing data scenario
13. Test Docker deployment
14. Verify all success criteria

**Total Time**: ~90 minutes

## 🎨 User Experience

### Before (Current)
```
User visits site
↓
Empty dashboard (no data)
↓
User manually starts scheduler
↓
User waits days for trends
↓
Maybe never comes back
```

### After (New)
```
User visits site
↓
Dashboard shows current market data
↓
Trends are immediately visible
↓
Data updates automatically daily
↓
User gets immediate value!
```

## 🔐 Security Considerations

1. **No Scheduler Controls**: Users can't start/stop scraping
2. **Read-Only Status**: Users can see when data was updated
3. **Admin Access** (optional): Protected admin routes for emergency control
4. **Rate Limiting**: Automatic scheduling prevents abuse
5. **Resource Management**: Single scheduler instance prevents overload

## 💡 Additional Enhancements (Future)

- [ ] Configurable schedule via environment variables
- [ ] Multiple scraping times per day
- [ ] Notification on scrape completion
- [ ] Admin dashboard for scheduler management
- [ ] Scraping statistics and metrics
- [ ] Retry failed scrapes automatically
- [ ] Email alerts on scraping errors

## 📋 Files to Create/Modify

### Create:
- `backend/seed_data.py` (new) - ~150 lines

### Modify:
- `backend/services/scheduler_service.py` - Add auto-initialize
- `backend/main.py` - Add startup event, remove/modify endpoints
- `frontend/index.html` - Remove controls, add status display
- `README.md` - Document automatic scheduling
- `DOCKER_DEPLOYMENT.md` - Note auto-start behavior
- `docs/user_guide.md` - Explain refresh schedule

### Update Tests:
- `backend/tests/test_scheduler.py` - Test auto-start
- `backend/tests/test_e2e.py` - Update scheduler tests

## ✅ Definition of Done

- [ ] `seed_data.py` created and tested
- [ ] Scheduler auto-starts on app launch
- [ ] Initial data seeding works on fresh deploy
- [ ] Frontend updated (no manual controls)
- [ ] Documentation updated (all 3 files)
- [ ] Tests updated and passing
- [ ] Fresh deployment tested
- [ ] Docker deployment tested
- [ ] No manual intervention needed
- [ ] All success criteria met

---

## 🚀 Ready to Implement?

Once approved, I will:
1. Create the data seeding script
2. Modify scheduler for auto-start
3. Update main app startup
4. Update frontend UI
5. Update all documentation
6. Run comprehensive tests
7. Verify everything works

**Estimated completion**: 90 minutes

**User experience improvement**: Immediate! ⚡

