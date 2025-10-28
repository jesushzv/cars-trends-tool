"""
Migration Script: Add Lifecycle Tracking Columns
Phase 19.6: Add first_seen and last_seen columns to listings table

This migration adds:
- first_seen: DateTime when listing was first discovered
- last_seen: DateTime when listing was last seen active

For existing listings, we'll backfill:
- first_seen = scraped_at (best estimate)
- last_seen = scraped_at (best estimate)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, Column, DateTime, text
from sqlalchemy.orm import sessionmaker
from database import DATABASE_URL
from models import Listing
from datetime import datetime

print("=" * 70)
print("MIGRATION: Add Lifecycle Tracking Columns to Listings")
print("=" * 70)
print()

# Connect to database
print(f"Connecting to database...")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

try:
    # Check if columns already exist
    print("Checking if columns already exist...")
    
    # Try PostgreSQL first, then SQLite
    try:
        # PostgreSQL query
        result = session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='listings'
        """))
        columns = [row[0] for row in result.fetchall()]
    except:
        # SQLite query
        result = session.execute(text("PRAGMA table_info(listings)"))
        columns = [row[1] for row in result.fetchall()]
    
    has_first_seen = 'first_seen' in columns
    has_last_seen = 'last_seen' in columns
    
    if has_first_seen and has_last_seen:
        print("✅ Columns already exist - no migration needed")
        sys.exit(0)
    
    # Determine column type based on database
    # PostgreSQL uses TIMESTAMP, SQLite uses DATETIME
    if 'postgresql' in DATABASE_URL.lower():
        datetime_type = 'TIMESTAMP'
    else:
        datetime_type = 'DATETIME'
    
    # Add columns if they don't exist
    if not has_first_seen:
        print(f"Adding 'first_seen' column ({datetime_type})...")
        session.execute(text(f"""
            ALTER TABLE listings 
            ADD COLUMN first_seen {datetime_type}
        """))
        session.commit()
        print("✅ Added 'first_seen' column")
    
    if not has_last_seen:
        print(f"Adding 'last_seen' column ({datetime_type})...")
        session.execute(text(f"""
            ALTER TABLE listings 
            ADD COLUMN last_seen {datetime_type}
        """))
        session.commit()
        print("✅ Added 'last_seen' column")
    
    # Backfill existing data
    print("\nBackfilling existing listings...")
    listings_count = session.query(Listing).count()
    print(f"Found {listings_count} existing listings")
    
    if listings_count > 0:
        # Update all existing listings
        # Set first_seen and last_seen to scraped_at as best estimate
        session.execute(text("""
            UPDATE listings 
            SET first_seen = scraped_at,
                last_seen = scraped_at
            WHERE first_seen IS NULL OR last_seen IS NULL
        """))
        session.commit()
        print(f"✅ Backfilled {listings_count} listings")
        print("   first_seen = scraped_at")
        print("   last_seen = scraped_at")
    
    # Create indexes for better query performance
    print("\nCreating indexes...")
    try:
        session.execute(text("CREATE INDEX IF NOT EXISTS idx_listings_first_seen ON listings(first_seen)"))
        session.execute(text("CREATE INDEX IF NOT EXISTS idx_listings_last_seen ON listings(last_seen)"))
        session.commit()
        print("✅ Created indexes on first_seen and last_seen")
    except Exception as e:
        print(f"⚠️  Index creation warning (may already exist): {e}")
    
    print()
    print("=" * 70)
    print("✅ MIGRATION COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  - Added lifecycle tracking columns")
    print(f"  - Backfilled {listings_count} existing listings")
    print(f"  - Created performance indexes")
    print()
    print("Next steps:")
    print("  - Scrapers will now track listing lifecycle")
    print("  - Cleanup job will use these timestamps")
    print()

except Exception as e:
    session.rollback()
    print(f"\n❌ ERROR: Migration failed")
    print(f"   {str(e)}")
    print()
    print("The database has been rolled back to previous state.")
    sys.exit(1)

finally:
    session.close()

