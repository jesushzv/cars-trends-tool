#!/usr/bin/env python3
"""
Migration Script: SQLite to PostgreSQL
Phase 17: PostgreSQL Migration

This script:
1. Reads all data from SQLite database
2. Creates tables in PostgreSQL
3. Inserts all data into PostgreSQL

Usage:
    python migrate_to_postgres.py
"""
import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Import models
from models import Base, Listing, DailySnapshot, User

# Database URLs
SQLITE_URL = "sqlite:///./listings.db"
POSTGRES_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://carstrends:carstrends@localhost:5432/carstrends"
)

def count_records(session, model):
    """Count records in a table"""
    return session.query(model).count()

def migrate():
    """Migrate data from SQLite to PostgreSQL"""
    print("=" * 70)
    print("MIGRATION: SQLite → PostgreSQL")
    print("=" * 70)
    print()
    
    # Check if SQLite database exists
    if not os.path.exists("listings.db"):
        print("❌ SQLite database (listings.db) not found!")
        print("   Nothing to migrate.")
        sys.exit(1)
    
    print(f"📂 Source: {SQLITE_URL}")
    print(f"📂 Target: {POSTGRES_URL}")
    print()
    
    # Create engines
    print("🔌 Connecting to databases...")
    try:
        sqlite_engine = create_engine(SQLITE_URL, echo=False)
        postgres_engine = create_engine(POSTGRES_URL, echo=False)
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print()
        print("Make sure PostgreSQL is running and configured correctly.")
        print("Run: ./setup_postgres.sh")
        sys.exit(1)
    
    # Test connections
    try:
        with sqlite_engine.connect() as conn:
            print("  ✅ Connected to SQLite")
        with postgres_engine.connect() as conn:
            print("  ✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"  ❌ Connection test failed: {e}")
        sys.exit(1)
    
    print()
    
    # Create sessions
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)
    
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    
    # Check if tables exist in SQLite
    inspector = inspect(sqlite_engine)
    sqlite_tables = inspector.get_table_names()
    
    print(f"📊 SQLite tables found: {', '.join(sqlite_tables)}")
    print()
    
    # Count records in SQLite
    print("📈 Counting records in SQLite...")
    stats = {}
    
    if 'listings' in sqlite_tables:
        listings_count = count_records(sqlite_session, Listing)
        stats['listings'] = listings_count
        print(f"  📋 Listings: {listings_count}")
    else:
        stats['listings'] = 0
        print(f"  📋 Listings: 0 (table not found)")
    
    if 'daily_snapshots' in sqlite_tables:
        snapshots_count = count_records(sqlite_session, DailySnapshot)
        stats['daily_snapshots'] = snapshots_count
        print(f"  📸 Daily Snapshots: {snapshots_count}")
    else:
        stats['daily_snapshots'] = 0
        print(f"  📸 Daily Snapshots: 0 (table not found)")
    
    if 'users' in sqlite_tables:
        users_count = count_records(sqlite_session, User)
        stats['users'] = users_count
        print(f"  👤 Users: {users_count}")
    else:
        stats['users'] = 0
        print(f"  👤 Users: 0 (table not found)")
    
    print()
    
    # Check if there's data to migrate
    total_records = sum(stats.values())
    if total_records == 0:
        print("⚠️  No data found in SQLite database.")
        print("   Creating empty PostgreSQL schema...")
        Base.metadata.create_all(postgres_engine)
        print("   ✅ PostgreSQL schema created")
        print()
        print("Migration complete (no data to migrate)")
        return
    
    # Confirm migration
    print(f"📦 Total records to migrate: {total_records}")
    print()
    
    # Drop and recreate PostgreSQL schema
    print("🗑️  Dropping existing PostgreSQL tables (if any)...")
    Base.metadata.drop_all(postgres_engine)
    print("  ✅ Tables dropped")
    
    print("🏗️  Creating PostgreSQL schema...")
    Base.metadata.create_all(postgres_engine)
    print("  ✅ Schema created")
    print()
    
    # Migrate data
    print("🚚 Migrating data...")
    print()
    
    # 1. Migrate Listings
    if stats['listings'] > 0:
        print(f"  📋 Migrating {stats['listings']} listings...")
        try:
            listings = sqlite_session.query(Listing).all()
            for listing in listings:
                # Create new listing without ID (let PostgreSQL auto-generate)
                new_listing = Listing(
                    platform=listing.platform,
                    title=listing.title,
                    url=listing.url,
                    price=listing.price,
                    location=listing.location,
                    posted_date=listing.posted_date,
                    scraped_at=listing.scraped_at,
                    year=listing.year,
                    make=listing.make,
                    model=listing.model,
                    mileage=listing.mileage
                )
                postgres_session.add(new_listing)
            
            postgres_session.commit()
            migrated_count = count_records(postgres_session, Listing)
            print(f"     ✅ Migrated {migrated_count} listings")
        except Exception as e:
            postgres_session.rollback()
            print(f"     ❌ Error: {e}")
    
    # 2. Migrate Daily Snapshots
    if stats['daily_snapshots'] > 0:
        print(f"  📸 Migrating {stats['daily_snapshots']} daily snapshots...")
        try:
            snapshots = sqlite_session.query(DailySnapshot).all()
            for snapshot in snapshots:
                new_snapshot = DailySnapshot(
                    date=snapshot.date,
                    make=snapshot.make,
                    model=snapshot.model,
                    avg_price=snapshot.avg_price,
                    min_price=snapshot.min_price,
                    max_price=snapshot.max_price,
                    listing_count=snapshot.listing_count,
                    craigslist_count=snapshot.craigslist_count,
                    mercadolibre_count=snapshot.mercadolibre_count,
                    facebook_count=snapshot.facebook_count,
                    created_at=snapshot.created_at
                )
                postgres_session.add(new_snapshot)
            
            postgres_session.commit()
            migrated_count = count_records(postgres_session, DailySnapshot)
            print(f"     ✅ Migrated {migrated_count} snapshots")
        except Exception as e:
            postgres_session.rollback()
            print(f"     ❌ Error: {e}")
    
    # 3. Migrate Users
    if stats['users'] > 0:
        print(f"  👤 Migrating {stats['users']} users...")
        try:
            users = sqlite_session.query(User).all()
            for user in users:
                new_user = User(
                    email=user.email,
                    username=user.username,
                    hashed_password=user.hashed_password,
                    is_active=user.is_active,
                    is_admin=user.is_admin,
                    created_at=user.created_at,
                    last_login=user.last_login
                )
                postgres_session.add(new_user)
            
            postgres_session.commit()
            migrated_count = count_records(postgres_session, User)
            print(f"     ✅ Migrated {migrated_count} users")
        except Exception as e:
            postgres_session.rollback()
            print(f"     ❌ Error: {e}")
    
    print()
    
    # Verify migration
    print("🔍 Verifying migration...")
    postgres_listings = count_records(postgres_session, Listing)
    postgres_snapshots = count_records(postgres_session, DailySnapshot)
    postgres_users = count_records(postgres_session, User)
    
    print(f"  📋 Listings: {stats['listings']} → {postgres_listings}")
    print(f"  📸 Snapshots: {stats['daily_snapshots']} → {postgres_snapshots}")
    print(f"  👤 Users: {stats['users']} → {postgres_users}")
    print()
    
    # Check if all data was migrated
    success = (
        postgres_listings == stats['listings'] and
        postgres_snapshots == stats['daily_snapshots'] and
        postgres_users == stats['users']
    )
    
    if success:
        print("=" * 70)
        print("✅ MIGRATION SUCCESSFUL!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Update .env or environment: export DATABASE_URL='postgresql://...'")
        print("  2. Start the application: python main.py")
        print("  3. Run tests: python -m pytest tests/")
        print()
    else:
        print("=" * 70)
        print("⚠️  MIGRATION COMPLETED WITH WARNINGS")
        print("=" * 70)
        print()
        print("Some records may not have been migrated.")
        print("Please review the logs above.")
        print()
    
    # Close sessions
    sqlite_session.close()
    postgres_session.close()

if __name__ == "__main__":
    try:
        migrate()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

