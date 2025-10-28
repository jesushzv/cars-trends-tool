"""
Listing Lifecycle Service
Phase 19.6: Handle listing lifecycle tracking

This service manages the lifecycle of listings:
- Track when listings are first seen
- Update when listings are seen again
- Detect price changes
- Enable duplicate detection
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Listing
from database import SessionLocal
import logging

logger = logging.getLogger(__name__)


def upsert_listing(listing_data: dict) -> Listing:
    """
    Insert or update a listing based on URL (unique identifier)
    
    If URL exists:
        - Update last_seen timestamp
        - Update price if changed
        - Keep first_seen unchanged
    
    If URL doesn't exist:
        - Create new listing
        - Set first_seen = last_seen = now
    
    Args:
        listing_data: Dictionary with listing fields
        Must include 'url' key
    
    Returns:
        Listing object (created or updated)
    """
    db = SessionLocal()
    now = datetime.utcnow()
    
    try:
        url = listing_data.get('url')
        if not url:
            raise ValueError("URL is required for upsert_listing")
        
        # Check if listing already exists
        existing = db.query(Listing).filter(Listing.url == url).first()
        
        if existing:
            # Update existing listing
            logger.info(f"Updating existing listing: {url[:50]}...")
            
            # Update last_seen
            existing.last_seen = now
            existing.scraped_at = now  # Also update scraped_at for compatibility
            
            # Update other fields that might change
            if 'price' in listing_data and listing_data['price'] != existing.price:
                old_price = existing.price
                existing.price = listing_data['price']
                logger.info(f"  Price changed: ${old_price} → ${listing_data['price']}")
            
            # Update engagement metrics if present
            if 'views' in listing_data:
                existing.views = listing_data['views']
            if 'likes' in listing_data:
                existing.likes = listing_data['likes']
            if 'comments' in listing_data:
                existing.comments = listing_data['comments']
            
            # Update title if changed (listings sometimes get re-titled)
            if 'title' in listing_data:
                existing.title = listing_data['title']
            
            db.commit()
            db.refresh(existing)
            return existing
        
        else:
            # Create new listing
            logger.info(f"Creating new listing: {url[:50]}...")
            
            # Set lifecycle timestamps
            listing_data['first_seen'] = now
            listing_data['last_seen'] = now
            listing_data['scraped_at'] = now
            
            new_listing = Listing(**listing_data)
            db.add(new_listing)
            db.commit()
            db.refresh(new_listing)
            return new_listing
    
    except IntegrityError as e:
        # Handle race condition (rare: two scrapers creating same URL simultaneously)
        db.rollback()
        logger.warning(f"IntegrityError (race condition?): {e}")
        # Try to fetch the now-existing listing
        existing = db.query(Listing).filter(Listing.url == listing_data['url']).first()
        if existing:
            existing.last_seen = now
            db.commit()
            return existing
        raise
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error upserting listing: {e}")
        raise
    
    finally:
        db.close()


def get_active_listings(days_old=7) -> list:
    """
    Get listings that were last seen recently
    
    Args:
        days_old: Consider listings active if seen within this many days
    
    Returns:
        List of active Listing objects
    """
    db = SessionLocal()
    
    try:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days_old)
        
        active = db.query(Listing).filter(
            Listing.last_seen >= cutoff
        ).all()
        
        return active
    
    finally:
        db.close()


def get_inactive_listings(days_old=7) -> list:
    """
    Get listings that haven't been seen recently (likely sold/removed)
    
    Args:
        days_old: Consider listings inactive if not seen for this many days
    
    Returns:
        List of inactive Listing objects
    """
    db = SessionLocal()
    
    try:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days_old)
        
        inactive = db.query(Listing).filter(
            Listing.last_seen < cutoff
        ).all()
        
        return inactive
    
    finally:
        db.close()


def get_listing_stats() -> dict:
    """
    Get statistics about listing lifecycle
    
    Returns:
        Dict with stats about active/inactive listings
    """
    db = SessionLocal()
    
    try:
        from datetime import timedelta
        from sqlalchemy import func
        
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        
        total = db.query(Listing).count()
        active = db.query(Listing).filter(Listing.last_seen >= week_ago).count()
        inactive = total - active
        
        avg_days_active = db.query(
            func.avg(
                func.julianday(Listing.last_seen) - func.julianday(Listing.first_seen)
            )
        ).scalar() or 0
        
        return {
            "total_listings": total,
            "active_last_7_days": active,
            "inactive_7_days": inactive,
            "average_days_active": round(avg_days_active, 1)
        }
    
    finally:
        db.close()


# ============================================================================
# TESTING
# ============================================================================
if __name__ == "__main__":
    print("Testing Listing Lifecycle Service...")
    print("=" * 60)
    
    # Test 1: Create new listing
    print("\n1. Creating new test listing...")
    test_listing = {
        'platform': 'test',
        'title': 'Test Car 2020',
        'url': 'http://test.com/car/12345',
        'price': 15000.0,
        'make': 'Honda',
        'model': 'Civic',
        'year': 2020,
        'mileage': 50000
    }
    
    created = upsert_listing(test_listing)
    print(f"   Created: {created.id}")
    print(f"   First seen: {created.first_seen}")
    print(f"   Last seen: {created.last_seen}")
    
    # Test 2: Update existing listing
    print("\n2. Updating existing listing...")
    import time
    time.sleep(1)  # Wait a second
    test_listing['price'] = 14500.0  # Price drop
    updated = upsert_listing(test_listing)
    print(f"   Updated: {updated.id}")
    print(f"   First seen: {updated.first_seen} (should be unchanged)")
    print(f"   Last seen: {updated.last_seen} (should be newer)")
    print(f"   Price: ${updated.price} (should be 14500)")
    
    # Test 3: Get stats
    print("\n3. Getting lifecycle stats...")
    stats = get_listing_stats()
    print(f"   Total listings: {stats['total_listings']}")
    print(f"   Active (7 days): {stats['active_last_7_days']}")
    print(f"   Inactive (7+ days): {stats['inactive_7_days']}")
    
    print("\n" + "=" * 60)
    print("✅ Tests complete!")

