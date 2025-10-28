# Phase 19.6: Automatic Scheduling & Data Retention

## ✅ Completed

**Goal**: Implement fully automated daily scraping with historical data tracking and retention policies.

## 🎯 Key Features Implemented

### 1. Listing Lifecycle Tracking
**Problem**: Previously, duplicate listings were skipped entirely, losing historical information.

**Solution**: Implemented lifecycle tracking with `first_seen` and `last_seen` timestamps.

**Changes**:
- **`models.py`**: Added `first_seen` and `last_seen` columns to `Listing` model
- **`migrate_add_lifecycle.py`**: Migration script to add columns to existing databases
- **`services/listing_lifecycle_service.py`**: New service for upsert logic
  - `upsert_listing()`: Create or update listings based on URL
  - Tracks price changes over time
  - Updates engagement metrics on subsequent scrapes
- **`db_service.py`**: Updated to use upsert instead of skip-on-duplicate

**Behavior**:
```
Day 1: Find Honda Civic at $15,000 → first_seen = last_seen = Day 1
Day 2: Still listed at $15,000 → last_seen = Day 2 (first_seen unchanged)
Day 3: Price drops to $14,500 → last_seen = Day 3, price updated, logged
Day 91: Cleanup runs → Remove if not seen in 90 days
```

### 2. Data Retention & Cleanup
**Problem**: Without cleanup, database would grow indefinitely.

**Solution**: Automated cleanup service with configurable retention periods.

**Changes**:
- **`services/cleanup_service.py`**: New service for data retention
  - `cleanup_old_listings()`: Remove listings last seen > X days ago
  - `cleanup_old_snapshots()`: Remove snapshots > Y days old
  - `cleanup_all()`: Run all cleanup operations
  - `get_cleanup_stats()`: View data age statistics

**Configuration** (Environment variables):
- `LISTING_RETENTION_DAYS=90` (default)
- `SNAPSHOT_RETENTION_DAYS=180` (default, 2x listings)

**Schedule**: Daily at 6:00 AM (Tijuana time)

### 3. Automatic Initial Data Seeding
**Problem**: New deployments showed empty dashboard until first scrape.

**Solution**: Automatic data seeding on first startup.

**Changes**:
- **`seed_data.py`**: Initial data population script
  - Checks if database is empty
  - Runs full scrape of all platforms if needed
  - Creates initial daily snapshot
  - Fails gracefully if platforms unavailable
  - **Special handling**: Facebook failures trigger alerting (per user requirement)

**Behavior**:
```
First startup → Database empty → Seed with initial scrape → Users see data immediately
Subsequent startups → Database has data → Skip seeding → Continue normal operation
```

### 4. Automatic Scheduler Startup
**Problem**: Manual scheduler start/stop was required.

**Solution**: Scheduler auto-starts on application launch.

**Changes**:
- **`services/scheduler_service.py`**: Enhanced scheduler
  - Added `_cleanup_job()` function for daily cleanup
  - Added `_facebook_failure_alert()` for alerting (per user requirement)
  - Updated `initialize_scheduler(auto_start=True)` to auto-start by default
  - Now schedules 5 jobs:
    1. 2:00 AM - Scrape Craigslist
    2. 3:00 AM - Scrape Mercado Libre
    3. 4:00 AM - Scrape Facebook (with alerting on failure)
    4. 5:00 AM - Create Daily Snapshot
    5. 6:00 AM - Cleanup Old Data (NEW)

- **`main.py`**: Enhanced startup event
  ```python
  @app.on_event("startup")
  def startup_event():
      1. Create database tables
      2. Seed initial data if empty
      3. Initialize and auto-start scheduler
  ```

### 5. Frontend Updates
**Problem**: Manual scheduler controls no longer needed/wanted.

**Solution**: Removed controls, kept read-only status display.

**Changes**:
- **`frontend/index.html`**:
  - ❌ Removed: Start/Stop/Refresh buttons
  - ❌ Removed: `startScheduler()` and `stopScheduler()` functions
  - ✅ Kept: Status display (read-only)
  - ✅ Added: Informative message "Scraping runs automatically every day at 2-4 AM"
  - ✅ Updated: Status shows next scheduled job

**User Experience**:
- Users see scheduler is "Active" with next run time
- No manual intervention needed or possible
- Clear expectation: data updates automatically overnight

## 📊 Data Flow

```
┌─────────────────────────────────────────┐
│     Application Startup                 │
├─────────────────────────────────────────┤
│  1. Create tables                       │
│  2. Check if DB empty                   │
│  3. If empty → Seed initial data        │
│  4. Initialize scheduler (auto-start)   │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│     Daily Operations (Automated)        │
├─────────────────────────────────────────┤
│  2 AM: Scrape Craigslist               │
│  3 AM: Scrape Mercado Libre            │
│  4 AM: Scrape Facebook (alert on fail) │
│  5 AM: Create daily snapshot           │
│  6 AM: Cleanup old data                │
│                                         │
│  For each listing:                      │
│    - URL exists? → Update last_seen    │
│    - URL new? → Create with timestamps │
│    - Price changed? → Log & update     │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│     Data Retention                      │
├─────────────────────────────────────────┤
│  Listings: Keep 90 days                │
│  Snapshots: Keep 180 days              │
│  Cleanup: Runs daily at 6 AM           │
│  Database: Size stays bounded          │
└─────────────────────────────────────────┘
```

## 🗄️ Database Schema Changes

### Listing Table (Updated)
```sql
CREATE TABLE listings (
    -- Existing columns...
    first_seen TIMESTAMP,      -- When first discovered (NEW)
    last_seen TIMESTAMP,       -- When last seen active (NEW)
    scraped_at TIMESTAMP       -- Deprecated, kept for compatibility
);
```

## 🔍 Key Decisions

| Decision | Option Chosen | Rationale |
|----------|---------------|-----------|
| **Duplicate Handling** | Option B: Lifecycle tracking | Track listing lifetime and price changes |
| **Listing Retention** | 90 days | Quarterly trends, industry standard |
| **Snapshot Retention** | 180 days (2x listings) | Snapshots are small, valuable for long-term trends |
| **Cleanup Schedule** | Daily at 6 AM | Automated, runs when traffic is low |
| **Initial Seeding** | Single scrape on first deploy | Immediate value for users |
| **Scraping Frequency** | Once daily | Perfect for market trend analysis |
| **Facebook Failures** | Fail gracefully + alerting | Comprehensive logging for troubleshooting |
| **Scheduler Controls** | Remove (read-only status only) | Fully automated, no manual intervention |

## 📝 Configuration

Add to `.env`:
```bash
# Data retention (optional, defaults shown)
LISTING_RETENTION_DAYS=90
SNAPSHOT_RETENTION_DAYS=180
```

## 🧪 Testing

Run migration:
```bash
cd backend
python migrate_add_lifecycle.py
```

Test lifecycle service:
```bash
python services/listing_lifecycle_service.py
```

Test cleanup service:
```bash
python services/cleanup_service.py
```

Test seed script:
```bash
python seed_data.py
```

Start application (auto-seeds and auto-starts scheduler):
```bash
uvicorn main:app --reload
```

## 📚 API Endpoints

### Unchanged (Still Available)
- `GET /scheduler/status` - View scheduler status (read-only)

### Removed
- ~~`POST /scheduler/start`~~ - No longer needed (auto-starts)
- ~~`POST /scheduler/stop`~~ - No longer needed (always running)

## ✅ Success Criteria

- [x] ~~Listings table~~ → Has `first_seen` and `last_seen` columns
- [x] Scrapers → Use upsert logic (update existing URLs)
- [x] Cleanup service → Removes old data automatically
- [x] Seed script → Populates empty database
- [x] Scheduler → Auto-starts on app launch
- [x] Scheduler → Includes cleanup job at 6 AM
- [x] Frontend → Shows read-only status (no controls)
- [x] Facebook failures → Trigger comprehensive alerting
- [x] Database size → Stays bounded (90-day retention)
- [x] Users → See data immediately on fresh deploys

## 🎯 User Experience

### Before Phase 19.6
1. Deploy application
2. Dashboard is empty
3. Manually start scheduler
4. Wait for first scrape
5. Duplicates skipped (no history)
6. Database grows forever

### After Phase 19.6
1. Deploy application
2. **Dashboard has data immediately** (auto-seeded)
3. **Scheduler already running** (auto-started)
4. Daily updates happen automatically
5. **Historical data tracked** (lifecycle)
6. **Database size managed** (cleanup)
7. No manual intervention needed

## 🚀 Next Phase Suggestions

1. **Cloud Deployment** (Phase 20)
   - Deploy to cloud platform
   - Set up production database
   - Configure production secrets
   
2. **Monitoring & Alerts** (Future Phase)
   - Email alerts for Facebook failures
   - Dashboard health checks
   - Scraping success metrics
   
3. **Advanced Analytics** (Future Phase)
   - Days on market analysis
   - Price change alerts
   - Sold listings tracking

## 📖 Files Created/Modified

### New Files
- `backend/services/listing_lifecycle_service.py`
- `backend/services/cleanup_service.py`
- `backend/seed_data.py`
- `backend/migrate_add_lifecycle.py`
- `PHASE_19.6_AUTO_SCHEDULING_REVISED_DESIGN.md`
- `PHASE_19.6_SUMMARY.md` (this file)

### Modified Files
- `backend/models.py` - Added lifecycle columns
- `backend/db_service.py` - Use upsert logic
- `backend/services/scheduler_service.py` - Auto-start, cleanup job, alerting
- `backend/main.py` - Enhanced startup event
- `frontend/index.html` - Removed controls, updated status display

### Configuration
- `.env` - Add `LISTING_RETENTION_DAYS`, `SNAPSHOT_RETENTION_DAYS`

## 🎉 Phase 19.6 Complete!

All requirements implemented and tested. The application now:
- ✅ Runs fully automated daily scraping
- ✅ Preserves historical data with lifecycle tracking
- ✅ Manages database size with retention policies
- ✅ Seeds initial data on first deployment
- ✅ Auto-starts scheduler (no manual control needed)
- ✅ Alerts on Facebook scraping failures
- ✅ Provides clear user experience

**Ready for cloud deployment (Phase 20)!** 🚀

