"""
Cleanup Service
Phase 19.6: Data retention and cleanup

Handles removal of old data based on retention policies:
- Listings older than X days
- Snapshots older than Y days
- Configurable retention periods
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Listing, DailySnapshot
from database import SessionLocal
import logging

logger = logging.getLogger(__name__)

# Configuration from environment variables with defaults
LISTING_RETENTION_DAYS = int(os.getenv("LISTING_RETENTION_DAYS", "90"))
SNAPSHOT_RETENTION_DAYS = int(os.getenv("SNAPSHOT_RETENTION_DAYS", "180"))


def cleanup_old_listings(retention_days: int = None) -> dict:
    """
    Remove listings older than retention_days
    
    Uses last_seen timestamp to determine if listing is old.
    This removes listings that haven't been seen during scraping
    for more than retention_days.
    
    Args:
        retention_days: Days to keep (default from env or 90)
    
    Returns:
        Dict with cleanup statistics
    """
    if retention_days is None:
        retention_days = LISTING_RETENTION_DAYS
    
    db = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        logger.info(f"Starting listings cleanup (retention: {retention_days} days)")
        logger.info(f"Removing listings last seen before: {cutoff_date}")
        
        # Count listings to be deleted
        to_delete = db.query(Listing).filter(
            Listing.last_seen < cutoff_date
        ).count()
        
        if to_delete == 0:
            logger.info("No old listings to delete")
            return {
                "deleted_count": 0,
                "retention_days": retention_days,
                "cutoff_date": cutoff_date.isoformat()
            }
        
        # Delete old listings
        deleted = db.query(Listing).filter(
            Listing.last_seen < cutoff_date
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"✅ Deleted {deleted} old listings (last seen before {cutoff_date.date()})")
        
        # Get remaining count
        remaining = db.query(Listing).count()
        logger.info(f"   Remaining listings: {remaining}")
        
        return {
            "deleted_count": deleted,
            "remaining_count": remaining,
            "retention_days": retention_days,
            "cutoff_date": cutoff_date.isoformat()
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error during listings cleanup: {e}")
        raise
    
    finally:
        db.close()


def cleanup_old_snapshots(retention_days: int = None) -> dict:
    """
    Remove daily snapshots older than retention_days
    
    Args:
        retention_days: Days to keep (default from env or 180)
    
    Returns:
        Dict with cleanup statistics
    """
    if retention_days is None:
        retention_days = SNAPSHOT_RETENTION_DAYS
    
    db = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        logger.info(f"Starting snapshots cleanup (retention: {retention_days} days)")
        logger.info(f"Removing snapshots before: {cutoff_date.date()}")
        
        # Count snapshots to be deleted
        to_delete = db.query(DailySnapshot).filter(
            DailySnapshot.date < cutoff_date.date()
        ).count()
        
        if to_delete == 0:
            logger.info("No old snapshots to delete")
            return {
                "deleted_count": 0,
                "retention_days": retention_days,
                "cutoff_date": cutoff_date.date().isoformat()
            }
        
        # Delete old snapshots
        deleted = db.query(DailySnapshot).filter(
            DailySnapshot.date < cutoff_date.date()
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"✅ Deleted {deleted} old snapshots (before {cutoff_date.date()})")
        
        # Get remaining count
        remaining = db.query(DailySnapshot).count()
        logger.info(f"   Remaining snapshots: {remaining}")
        
        return {
            "deleted_count": deleted,
            "remaining_count": remaining,
            "retention_days": retention_days,
            "cutoff_date": cutoff_date.date().isoformat()
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error during snapshots cleanup: {e}")
        raise
    
    finally:
        db.close()


def cleanup_all() -> dict:
    """
    Run all cleanup operations
    
    Returns:
        Dict with combined cleanup statistics
    """
    logger.info("=" * 70)
    logger.info("STARTING SCHEDULED CLEANUP")
    logger.info("=" * 70)
    
    listings_result = cleanup_old_listings()
    snapshots_result = cleanup_old_snapshots()
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "listings": listings_result,
        "snapshots": snapshots_result,
        "total_deleted": listings_result["deleted_count"] + snapshots_result["deleted_count"]
    }
    
    logger.info("=" * 70)
    logger.info(f"CLEANUP COMPLETE - Total deleted: {result['total_deleted']}")
    logger.info("=" * 70)
    
    return result


def get_cleanup_stats() -> dict:
    """
    Get statistics about data age and cleanup needs
    
    Returns:
        Dict with statistics about data age
    """
    db = SessionLocal()
    
    try:
        from sqlalchemy import func
        
        # Listings statistics
        total_listings = db.query(Listing).count()
        oldest_listing = db.query(func.min(Listing.last_seen)).scalar()
        newest_listing = db.query(func.max(Listing.last_seen)).scalar()
        
        # Listings by age
        now = datetime.utcnow()
        week_cutoff = now - timedelta(days=7)
        month_cutoff = now - timedelta(days=30)
        quarter_cutoff = now - timedelta(days=90)
        
        last_week = db.query(Listing).filter(Listing.last_seen >= week_cutoff).count()
        last_month = db.query(Listing).filter(Listing.last_seen >= month_cutoff).count()
        last_quarter = db.query(Listing).filter(Listing.last_seen >= quarter_cutoff).count()
        older = total_listings - last_quarter
        
        # Snapshots statistics
        total_snapshots = db.query(DailySnapshot).count()
        oldest_snapshot = db.query(func.min(DailySnapshot.date)).scalar()
        newest_snapshot = db.query(func.max(DailySnapshot.date)).scalar()
        
        return {
            "listings": {
                "total": total_listings,
                "last_7_days": last_week,
                "last_30_days": last_month,
                "last_90_days": last_quarter,
                "older_than_90_days": older,
                "oldest_date": oldest_listing.isoformat() if oldest_listing else None,
                "newest_date": newest_listing.isoformat() if newest_listing else None
            },
            "snapshots": {
                "total": total_snapshots,
                "oldest_date": oldest_snapshot.isoformat() if oldest_snapshot else None,
                "newest_date": newest_snapshot.isoformat() if newest_snapshot else None
            },
            "retention_policy": {
                "listings_days": LISTING_RETENTION_DAYS,
                "snapshots_days": SNAPSHOT_RETENTION_DAYS
            }
        }
    
    finally:
        db.close()


# ============================================================================
# TESTING
# ============================================================================
if __name__ == "__main__":
    print("Testing Cleanup Service...")
    print("=" * 70)
    
    # Test 1: Get current stats
    print("\n1. Current data statistics:")
    stats = get_cleanup_stats()
    print(f"   Total listings: {stats['listings']['total']}")
    print(f"   Last 7 days: {stats['listings']['last_7_days']}")
    print(f"   Last 90 days: {stats['listings']['last_90_days']}")
    print(f"   Older than 90 days: {stats['listings']['older_than_90_days']}")
    print(f"   Total snapshots: {stats['snapshots']['total']}")
    print(f"   Retention policy: {stats['retention_policy']}")
    
    # Test 2: Dry run cleanup (show what would be deleted)
    print("\n2. What would be deleted with current retention policy:")
    print(f"   Listings retention: {LISTING_RETENTION_DAYS} days")
    print(f"   Snapshots retention: {SNAPSHOT_RETENTION_DAYS} days")
    
    # Test 3: Run actual cleanup
    print("\n3. Running cleanup...")
    result = cleanup_all()
    print(f"   ✅ Deleted {result['listings']['deleted_count']} old listings")
    print(f"   ✅ Deleted {result['snapshots']['deleted_count']} old snapshots")
    print(f"   Total deleted: {result['total_deleted']}")
    
    print("\n" + "=" * 70)
    print("✅ Tests complete!")

