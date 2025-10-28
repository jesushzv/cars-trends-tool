# Phase 19.6: Automatic Scheduling & Data Retention - REVISED Design

## 🎯 Clarified Requirements

1. **Daily Scraping**: Run automatically once per day
2. **Preserve Historical Data**: Keep old listings for trend analysis
3. **Data Retention Policy**: Drop data older than X days
4. **Initial Seeding**: Pre-populate with first scrape

## 📊 Data Flow Understanding

```
Day 1: Scrape → Store 100 listings → Database: 100 listings
Day 2: Scrape → Store 105 listings → Database: 205 listings (keep both days)
Day 3: Scrape → Store 98 listings  → Database: 303 listings (keep all three days)
...
Day 91: Scrape → Store 110 listings → Database: Keep 90 days, drop day 1
```

## 🔑 Key Concepts

### 1. Listings Table Strategy

**Current Schema**:
```python
class Listing:
    id
    platform
    title
    url
    price
    make
    model
    year
    mileage
    scraped_at  # Timestamp when scraped
```

**Question**: How do we handle duplicates?

**Option A**: Keep all scrapes (duplicates allowed)
- Same car scraped daily = multiple entries
- Pro: Simple, complete history
- Con: Database grows fast, duplicates

**Option B**: Update existing listings
- Same URL = update existing entry
- Add `first_seen` and `last_seen` timestamps
- Track price changes over time
- Pro: Cleaner, track lifecycle
- Con: More complex logic

**Option C**: Hybrid approach
- New table: `listing_history` for price changes
- Main `listings` table has current state
- Pro: Best of both worlds
- Con: More tables to manage

### 2. Data Retention Policy

**Options for Retention Period**:
- 30 days: Good for short-term trends
- 60 days: Better for seasonal analysis
- 90 days: Comprehensive quarterly trends
- 180 days: Half-year trends
- 365 days: Full year trends

**Cleanup Strategy**:
```python
def cleanup_old_data(retention_days=90):
    """Remove listings older than retention_days"""
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    # Delete old listings
    db.query(Listing).filter(
        Listing.scraped_at < cutoff_date
    ).delete()
    
    # Keep daily snapshots longer (they're small)
    snapshot_retention = retention_days * 2  # Keep snapshots 2x longer
    snapshot_cutoff = datetime.now() - timedelta(days=snapshot_retention)
    
    db.query(DailySnapshot).filter(
        DailySnapshot.date < snapshot_cutoff
    ).delete()
```

**When to Run Cleanup**:
- Option A: After each daily scrape
- Option B: Separate weekly cleanup job
- Option C: On-demand (manual trigger)

### 3. Daily Snapshots

**Current Strategy**: Aggregate listings for trends
```python
DailySnapshot:
    date
    make
    model
    avg_price
    listing_count
    ...
```

**These are small and valuable** - keep longer than raw listings

**Recommended**: Keep snapshots for 2x the listing retention period

## 🎨 Revised Architecture

```
┌─────────────────────────────────────────┐
│     Application Startup                 │
├─────────────────────────────────────────┤
│  1. Initialize Database                 │
│  2. Check if listings exist             │
│  3. If empty → Run initial seed         │
│  4. Auto-start scheduler                │
│  5. Schedule daily jobs:                │
│     - 2 AM: Scrape Craigslist          │
│     - 3 AM: Scrape Mercado Libre       │
│     - 4 AM: Scrape Facebook            │
│     - 5 AM: Create daily snapshot      │
│     - 6 AM: Cleanup old data           │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│     Daily Operations                    │
├─────────────────────────────────────────┤
│  Daily at 2-6 AM:                       │
│    1. Scrape all platforms              │
│    2. Store NEW listings                │
│    3. Create daily snapshot             │
│    4. Remove old data (>X days)         │
│    5. Database stays bounded            │
│                                         │
│  All day:                               │
│    - Users see historical trends        │
│    - Price trends show changes          │
│    - Market analysis uses all data     │
└─────────────────────────────────────────┘
```

## 📝 Questions for You

### Question 1: Duplicate Handling Strategy
**How should we handle the same listing appearing on multiple days?**

**Example**: A 2020 Honda Civic listed at $15,000 on Monday, still there on Tuesday

**Option A - Keep All Scrapes**:
```
listings:
  id=1, url="...", price=15000, scraped_at="2025-10-28 02:00"
  id=2, url="...", price=15000, scraped_at="2025-10-29 02:00"  # Same listing, next day
  id=3, url="...", price=14500, scraped_at="2025-10-30 02:00"  # Same listing, price dropped
```
- ✅ Simple to implement
- ✅ Complete history
- ❌ Lots of duplicates
- ❌ Database grows fast

**Option B - Track Listing Lifecycle**:
```
listings:
  id=1, url="...", price=15000, first_seen="2025-10-28", last_seen="2025-10-30"
  
listing_price_history:
  listing_id=1, price=15000, date="2025-10-28"
  listing_id=1, price=15000, date="2025-10-29"
  listing_id=1, price=14500, date="2025-10-30"  # Price change tracked
```
- ✅ No duplicates
- ✅ Track lifecycle (new → active → sold)
- ✅ Track price changes
- ❌ More complex
- ❌ Need to match URLs across scrapes

**Option C - Hybrid (Current + History)**:
```
current_listings (main table):
  id=1, url="...", price=14500, last_updated="2025-10-30"
  
listings_archive:
  id=1, url="...", price=15000, scraped_at="2025-10-28"
  id=2, url="...", price=15000, scraped_at="2025-10-29"
```
- ✅ Current data clean
- ✅ Historical data preserved
- ❌ Most complex

**My Recommendation**: Option A for now (simplest), upgrade to B later if needed

---

### Question 2: Data Retention Period
**How long should we keep raw listing data?**

**Options**:
- **30 days**: Short-term trends, minimal storage
- **60 days**: Good balance, see monthly patterns
- **90 days**: Quarterly trends, industry standard
- **180 days**: Half-year trends, seasonal patterns
- **365 days**: Full year, best analysis

**My Recommendation**: 90 days for listings, 180 days for snapshots

**Rationale**:
- 90 days = ~3 months of market trends
- Snapshots are tiny, keep longer for historical trends
- Can always increase retention later
- Keeps database size manageable

---

### Question 3: Snapshot Retention
**How long should we keep daily snapshots?**

**Note**: Snapshots are small (one row per make/model per day)

**Options**:
- Same as listings (90 days)
- 2x listings (180 days)
- Indefinitely (they're small)

**My Recommendation**: 2x listing retention (180 days if listings are 90 days)

**Rationale**:
- Snapshots enable long-term trend analysis
- Very small storage footprint
- More valuable over time
- Can show year-over-year trends

---

### Question 4: Cleanup Schedule
**When should we run the cleanup job?**

**Options**:
- **Daily**: After scraping (6 AM)
- **Weekly**: Sunday at midnight
- **Monthly**: First day of month
- **On-demand**: Admin trigger only

**My Recommendation**: Daily at 6 AM (after all scraping and snapshot creation)

**Rationale**:
- Keeps database size consistent
- Part of automated daily routine
- No manual intervention needed
- Runs when traffic is low

---

### Question 5: Initial Seeding
**How much initial data should we seed?**

**Options**:
- **Single scrape**: Run once, get current listings
- **Multiple days**: Scrape, wait, scrape again (slower)
- **Backfill**: Scrape and create fake historical dates (not ideal)

**My Recommendation**: Single scrape on first deploy

**Rationale**:
- Get immediate data for users
- Real trends will develop over days naturally
- Can't fake historical data accurately
- Users understand "tracking started X days ago"

---

### Question 6: Scraping Frequency
**Confirm: Once per day is sufficient?**

**Current Plan**: 
- 2 AM: Craigslist
- 3 AM: Mercado Libre
- 4 AM: Facebook
- 5 AM: Snapshot
- 6 AM: Cleanup

**Alternative**: 
- Multiple times per day (morning + evening)?
- Different days for different platforms?

**My Recommendation**: Once per day is perfect for market trends

---

### Question 7: Storage Considerations
**What's your database size limit concern?**

**Rough Math** (90-day retention):
```
- 100 listings/day × 90 days = 9,000 listings
- ~1 KB per listing = ~9 MB
- Daily snapshots: ~100 rows/day × 90 days = 9,000 rows = ~1 MB
- Total: ~10-20 MB for 90 days

With PostgreSQL: Can easily handle gigabytes
With SQLite: Also fine for this volume
```

**Options**:
- SQLite: Good for <100K listings
- PostgreSQL: Good for millions of listings

**My Recommendation**: Current setup (SQLite or PostgreSQL) handles this easily

---

### Question 8: Facebook Cookies
**For initial seeding, how should we handle Facebook?**

**Options**:
- **Require cookies first**: Setup before deploy
- **Optional**: Seed without Facebook if cookies missing
- **Fail gracefully**: Try Facebook, continue if fails

**My Recommendation**: Option 3 (Try Facebook, continue if fails)

---

## 📦 Updated Implementation Plan

Based on your answers, I'll implement:

### 1. Data Model Changes (if needed)
- Option A: No changes (keep all scrapes)
- Option B: Add `first_seen`, `last_seen`, lifecycle tracking
- Option C: Add `listings_archive` table

### 2. Cleanup Service
```python
# New file: services/cleanup_service.py

def cleanup_old_listings(retention_days=90):
    """Remove listings older than retention_days"""
    cutoff = datetime.now() - timedelta(days=retention_days)
    deleted = db.query(Listing).filter(
        Listing.scraped_at < cutoff
    ).delete()
    logger.info(f"Deleted {deleted} old listings")

def cleanup_old_snapshots(retention_days=180):
    """Remove snapshots older than retention_days"""
    cutoff = datetime.now() - timedelta(days=retention_days)
    deleted = db.query(DailySnapshot).filter(
        DailySnapshot.date < cutoff
    ).delete()
    logger.info(f"Deleted {deleted} old snapshots")
```

### 3. Updated Scheduler
```python
# Add cleanup job to scheduler
scheduler.add_job(
    cleanup_old_listings,
    'cron',
    hour=6,
    minute=0,
    args=[90],  # Retention days from config
    id='cleanup_listings',
    name='Cleanup Old Listings'
)

scheduler.add_job(
    cleanup_old_snapshots,
    'cron',
    hour=6,
    minute=30,
    args=[180],
    id='cleanup_snapshots',
    name='Cleanup Old Snapshots'
)
```

### 4. Configuration
```python
# Add to environment variables
LISTING_RETENTION_DAYS=90
SNAPSHOT_RETENTION_DAYS=180
```

### 5. Seed Data Script
```python
# seed_data.py - initial population
def seed_initial_data():
    """Run initial scrape to populate database"""
    if count_listings() > 0:
        logger.info("Database has data, skipping seed")
        return
    
    logger.info("Running initial data seed...")
    
    # Scrape all platforms
    scrape_craigslist_tijuana()
    scrape_mercadolibre_tijuana()
    
    # Try Facebook (optional)
    try:
        scrape_facebook_tijuana()
    except Exception as e:
        logger.warning(f"Facebook scraping failed (ok): {e}")
    
    # Create first snapshot
    create_daily_snapshot()
    
    logger.info("Initial seed complete!")
```

---

## ✅ Summary of Questions

Please answer:

1. **Duplicate Handling**: Option A (keep all), B (lifecycle), or C (hybrid)?
2. **Listing Retention**: 30, 60, 90, 180, or 365 days?
3. **Snapshot Retention**: Same as listings, 2x, or indefinite?
4. **Cleanup Schedule**: Daily, weekly, monthly, or on-demand?
5. **Initial Seeding**: Single scrape ok?
6. **Scraping Frequency**: Once per day confirmed?
7. **Storage Concerns**: Any specific limits?
8. **Facebook Cookies**: Require, optional, or fail gracefully?

Once you answer these, I'll implement the complete solution! 🚀

