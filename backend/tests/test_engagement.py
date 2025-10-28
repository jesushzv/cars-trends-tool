"""
Phase 10: Tests for engagement metrics functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from models import Listing
from database import create_tables, SessionLocal
from db_service import save_listing, get_all_listings


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create fresh database tables before each test"""
    create_tables()
    yield
    # Cleanup after test
    db = SessionLocal()
    try:
        db.query(Listing).delete()
        db.commit()
    finally:
        db.close()


def test_listing_model_has_engagement_fields():
    """Test that Listing model has engagement columns"""
    listing = Listing(
        platform="mercadolibre",
        title="Test Car",
        url="https://test.com/car1",
        views=150,
        likes=25,
        comments=5
    )
    
    assert listing.views == 150
    assert listing.likes == 25
    assert listing.comments == 5


def test_save_listing_with_views():
    """Test saving a listing with views count"""
    result = save_listing(
        platform="mercadolibre",
        title="2023 Honda Accord",
        url="https://test.com/car2",
        price=25000.0,
        make="Honda",
        model="Accord",
        year=2023,
        mileage=15000,
        views=200
    )
    
    assert result is not None
    assert result.views == 200
    assert result.likes is None  # Not provided
    assert result.comments is None  # Not provided


def test_save_listing_with_all_engagement_metrics():
    """Test saving a listing with all engagement metrics"""
    result = save_listing(
        platform="mercadolibre",
        title="2024 Tesla Model 3",
        url="https://test.com/car3",
        price=45000.0,
        make="Tesla",
        model="Model 3",
        year=2024,
        mileage=5000,
        views=500,
        likes=75,
        comments=12
    )
    
    assert result is not None
    assert result.views == 500
    assert result.likes == 75
    assert result.comments == 12


def test_save_listing_without_engagement_metrics():
    """Test that listings can be saved without engagement metrics (backwards compatibility)"""
    result = save_listing(
        platform="craigslist",
        title="2020 Ford F-150",
        url="https://test.com/car4",
        price=32000.0,
        make="Ford",
        model="F-150",
        year=2020,
        mileage=45000
        # No engagement metrics provided
    )
    
    assert result is not None
    assert result.views is None
    assert result.likes is None
    assert result.comments is None


def test_get_listings_returns_engagement_data():
    """Test that querying listings returns engagement data"""
    # Save listing with engagement metrics
    save_listing(
        platform="mercadolibre",
        title="2023 BMW X5",
        url="https://test.com/car5",
        price=65000.0,
        make="BMW",
        model="X5",
        year=2023,
        mileage=12000,
        views=350,
        likes=45
    )
    
    # Query all listings
    listings = get_all_listings(limit=10)
    
    assert len(listings) == 1
    assert listings[0].views == 350
    assert listings[0].likes == 45
    assert listings[0].comments is None


def test_engagement_metrics_are_optional():
    """Test that None values are accepted for engagement metrics"""
    result = save_listing(
        platform="mercadolibre",
        title="2022 Toyota Camry",
        url="https://test.com/car6",
        price=28000.0,
        views=None,
        likes=None,
        comments=None
    )
    
    assert result is not None
    assert result.views is None
    assert result.likes is None
    assert result.comments is None


def test_large_engagement_numbers():
    """Test that large engagement numbers are handled correctly"""
    result = save_listing(
        platform="mercadolibre",
        title="Popular Listing",
        url="https://test.com/popular",
        price=50000.0,
        views=10000,
        likes=1500,
        comments=250
    )
    
    assert result is not None
    assert result.views == 10000
    assert result.likes == 1500
    assert result.comments == 250


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

