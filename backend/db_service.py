"""
Database service - functions for saving and querying listings
Phase 2: Simple CRUD operations
"""
from sqlalchemy.orm import Session
from models import Listing
from database import SessionLocal
from typing import List, Optional


def save_listing(platform: str, title: str, url: str, price: Optional[float] = None, 
                 make: Optional[str] = None, model: Optional[str] = None, 
                 year: Optional[int] = None, mileage: Optional[int] = None,
                 views: Optional[int] = None, likes: Optional[int] = None,
                 comments: Optional[int] = None) -> Optional[Listing]:
    """
    Save a single listing to the database
    Phase 4: Enhanced with car fields
    Phase 10: Enhanced with engagement metrics
    
    Args:
        platform: Platform name ('craigslist', 'mercadolibre', 'facebook')
        title: Listing title
        url: Listing URL
        price: Optional price
        make: Optional car make (e.g., 'Honda')
        model: Optional car model (e.g., 'Accord')
        year: Optional year (e.g., 2020)
        mileage: Optional mileage
        views: Optional number of views
        likes: Optional number of likes/favorites
        comments: Optional number of comments
        
    Returns:
        The saved Listing object with ID assigned, or None if duplicate URL
    """
    db = SessionLocal()
    try:
        # Check if URL already exists
        existing = db.query(Listing).filter(Listing.url == url).first()
        if existing:
            print(f"  [INFO] Duplicate URL skipped: {url}")
            return None
        
        listing = Listing(
            platform=platform,
            title=title,
            url=url,
            price=price,
            make=make,
            model=model,
            year=year,
            mileage=mileage,
            views=views,
            likes=likes,
            comments=comments
        )
        db.add(listing)
        db.commit()
        db.refresh(listing)
        return listing
    finally:
        db.close()


def get_all_listings(limit: int = 100) -> List[Listing]:
    """
    Query all listings from the database
    
    Args:
        limit: Maximum number of listings to return
        
    Returns:
        List of Listing objects
    """
    db = SessionLocal()
    try:
        listings = db.query(Listing).order_by(Listing.scraped_at.desc()).limit(limit).all()
        return listings
    finally:
        db.close()


def get_listings_by_platform(platform: str, limit: int = 100) -> List[Listing]:
    """
    Query listings filtered by platform
    
    Args:
        platform: Platform name to filter by
        limit: Maximum number of listings to return
        
    Returns:
        List of Listing objects from the specified platform
    """
    db = SessionLocal()
    try:
        listings = db.query(Listing).filter(
            Listing.platform == platform
        ).order_by(Listing.scraped_at.desc()).limit(limit).all()
        return listings
    finally:
        db.close()


def count_listings() -> int:
    """Count total number of listings in database"""
    db = SessionLocal()
    try:
        return db.query(Listing).count()
    finally:
        db.close()


if __name__ == "__main__":
    print("Testing database service...")
    
    # First, create tables
    from database import create_tables
    print("\n0. Creating tables...")
    create_tables()
    
    # Test saving a listing
    print("\n1. Saving a test listing...")
    listing = save_listing(
        platform="craigslist",
        title="2015 Honda Accord",
        url="https://tijuana.craigslist.org/test123",
        price=12000.0
    )
    print(f"✓ Saved: {listing}")
    print(f"  ID: {listing.id}")
    print(f"  Scraped at: {listing.scraped_at}")
    
    # Test querying all listings
    print("\n2. Querying all listings...")
    all_listings = get_all_listings()
    print(f"✓ Found {len(all_listings)} listings")
    for lst in all_listings:
        print(f"  - {lst}")
    
    # Test count
    print("\n3. Counting listings...")
    count = count_listings()
    print(f"✓ Total listings: {count}")
    
    # Test duplicate prevention
    print("\n4. Testing duplicate prevention...")
    duplicate = save_listing(
        platform="craigslist",
        title="2015 Honda Accord (duplicate)",
        url="https://tijuana.craigslist.org/test123",  # Same URL as before
        price=15000.0
    )
    if duplicate is None:
        print("✓ Duplicate correctly prevented")
    else:
        print("✗ ERROR: Duplicate was saved!")
    
    # Verify count didn't increase
    new_count = count_listings()
    print(f"  Listings count after duplicate attempt: {new_count}")
    if new_count == count:
        print("✓ Count unchanged (duplicate was skipped)")
    
    print("\n✅ All database operations working!")

