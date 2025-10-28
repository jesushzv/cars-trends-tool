"""
Database models
Phase 2: Listing model for storing scraped car listings
Phase 4: Enhanced with car-specific fields
Phase 10: Added engagement metrics
Phase 13: Added DailySnapshot model for price trends
Phase 16: Added User model for authentication
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, UniqueConstraint, Boolean
from datetime import datetime, date
from database import Base


class Listing(Base):
    """
    Car listing model - stores scraped listings from various platforms
    Phase 4: Added make, model, year, mileage fields
    Phase 10: Added engagement metrics (views, likes, comments)
    """
    __tablename__ = "listings"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Basic fields
    platform = Column(String(20), nullable=False, index=True)  # 'craigslist', 'mercadolibre', 'facebook'
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False, unique=True)  # Unique constraint to prevent duplicates
    
    # Price field
    price = Column(Float, nullable=True)  # Price can be missing
    
    # Car-specific fields (Phase 4)
    make = Column(String(50), nullable=True, index=True)  # e.g., 'Honda', 'Toyota'
    model = Column(String(100), nullable=True)  # e.g., 'Accord', 'Camry'
    year = Column(Integer, nullable=True, index=True)  # e.g., 2015
    mileage = Column(Integer, nullable=True)  # Miles/kilometers
    
    # Engagement metrics (Phase 10)
    views = Column(Integer, nullable=True)  # Number of views
    likes = Column(Integer, nullable=True)  # Number of likes/favorites
    comments = Column(Integer, nullable=True)  # Number of comments
    
    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # When we scraped it
    
    def __repr__(self):
        car_info = f"{self.year} {self.make} {self.model}" if self.year and self.make else self.title[:30]
        return f"<Listing {self.id}: {self.platform} - {car_info}>"


class DailySnapshot(Base):
    """
    Daily aggregated statistics for car market trends
    Phase 13: Track price changes over time
    
    Stores one record per day per make/model combination with:
    - Average price
    - Listing count
    - Price range (min/max)
    """
    __tablename__ = "daily_snapshots"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Date and car identifiers
    date = Column(Date, nullable=False, index=True)  # Snapshot date
    make = Column(String(50), nullable=False, index=True)  # e.g., 'Honda'
    model = Column(String(100), nullable=False, index=True)  # e.g., 'Civic'
    
    # Price statistics
    avg_price = Column(Float, nullable=True)  # Average price for this day
    min_price = Column(Float, nullable=True)  # Lowest price
    max_price = Column(Float, nullable=True)  # Highest price
    
    # Volume statistics
    listing_count = Column(Integer, nullable=False, default=0)  # Number of listings
    
    # Platform breakdown (optional)
    craigslist_count = Column(Integer, nullable=False, default=0)
    mercadolibre_count = Column(Integer, nullable=False, default=0)
    facebook_count = Column(Integer, nullable=False, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Ensure only one snapshot per day per make/model
    __table_args__ = (
        UniqueConstraint('date', 'make', 'model', name='unique_daily_snapshot'),
    )
    
    def __repr__(self):
        return f"<DailySnapshot {self.date}: {self.make} {self.model} - {self.listing_count} listings, avg ${self.avg_price}>"


class User(Base):
    """
    User model for authentication
    Phase 16: Authentication
    
    Stores user credentials and profile information
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # User status
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.id}: {self.username} ({self.email})>"


if __name__ == "__main__":
    # Test model instantiation
    print("Testing Listing model...")
    listing = Listing(
        platform="craigslist",
        title="2015 Honda Accord",
        url="https://tijuana.craigslist.org/test"
    )
    print(f"✓ Created listing: {listing}")
    print(f"  Platform: {listing.platform}")
    print(f"  Title: {listing.title}")
    print(f"  URL: {listing.url}")

