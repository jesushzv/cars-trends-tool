"""
Tests for Phase 13: Time Series - Price Trends
"""
import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Base, Listing, DailySnapshot
from services.trends_service import (
    create_daily_snapshot,
    get_price_trend,
    get_trending_cars,
    get_market_overview
)


@pytest.fixture(scope="function")
def test_db(monkeypatch):
    """Create a fresh test database for each test"""
    test_engine = create_engine("sqlite:///:memory:")
    TestSessionLocal = sessionmaker(bind=test_engine)
    
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    
    # Monkey patch SessionLocal in trends_service
    import services.trends_service
    monkeypatch.setattr('services.trends_service.SessionLocal', TestSessionLocal)
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def sample_listings(test_db):
    """Create sample listings for testing"""
    listings = [
        Listing(platform="craigslist", title="2020 Honda Civic", url="http://test1.com",
                make="Honda", model="Civic", year=2020, price=18000),
        Listing(platform="craigslist", title="2019 Honda Civic", url="http://test2.com",
                make="Honda", model="Civic", year=2019, price=16000),
        Listing(platform="mercadolibre", title="2021 Honda Civic", url="http://test3.com",
                make="Honda", model="Civic", year=2021, price=20000),
        Listing(platform="facebook", title="2018 Toyota Camry", url="http://test4.com",
                make="Toyota", model="Camry", year=2018, price=15000),
        Listing(platform="craigslist", title="2020 Toyota Camry", url="http://test5.com",
                make="Toyota", model="Camry", year=2020, price=19000),
    ]
    
    for listing in listings:
        test_db.add(listing)
    test_db.commit()
    
    return listings


class TestDailySnapshot:
    """Test daily snapshot creation"""
    
    def test_create_snapshot_with_data(self, test_db, sample_listings):
        """Test creating snapshot when listings exist"""
        result = create_daily_snapshot()
        
        assert result['snapshots_created'] == 2  # Honda Civic, Toyota Camry
        assert result['total_cars'] == 2
        assert 'date' in result
    
    def test_create_snapshot_empty_db(self, test_db):
        """Test creating snapshot with no data"""
        result = create_daily_snapshot()
        
        assert result['snapshots_created'] == 0
        assert result['total_cars'] == 0
    
    def test_snapshot_calculates_stats(self, test_db, sample_listings):
        """Test that snapshot calculates correct statistics"""
        create_daily_snapshot()
        
        # Check Honda Civic snapshot
        civic_snap = test_db.query(DailySnapshot).filter(
            DailySnapshot.make == 'Honda',
            DailySnapshot.model == 'Civic'
        ).first()
        
        assert civic_snap is not None
        assert civic_snap.listing_count == 3
        assert civic_snap.avg_price == 18000.0  # (18000 + 16000 + 20000) / 3
        assert civic_snap.min_price == 16000.0
        assert civic_snap.max_price == 20000.0
        assert civic_snap.craigslist_count == 2
        assert civic_snap.mercadolibre_count == 1
        assert civic_snap.facebook_count == 0
    
    def test_snapshot_update_existing(self, test_db, sample_listings):
        """Test that running snapshot twice updates existing records"""
        # First snapshot
        result1 = create_daily_snapshot()
        assert result1['snapshots_created'] == 2
        assert result1['snapshots_updated'] == 0
        
        # Second snapshot (should update)
        result2 = create_daily_snapshot()
        assert result2['snapshots_created'] == 0
        assert result2['snapshots_updated'] == 2


class TestPriceTrend:
    """Test price trend queries"""
    
    def test_get_trend_with_data(self, test_db, sample_listings):
        """Test getting price trend for a car"""
        # Create snapshots for multiple days
        today = date.today()
        for i in range(3):
            snapshot_date = today - timedelta(days=i)
            test_db.add(DailySnapshot(
                date=snapshot_date,
                make="Honda",
                model="Civic",
                listing_count=10 + i,
                avg_price=18000 + (i * 100),
                min_price=16000,
                max_price=20000
            ))
        test_db.commit()
        
        # Get trend
        trend = get_price_trend("Honda", "Civic", days=7)
        
        assert len(trend) == 3
        assert all('date' in t for t in trend)
        assert all('avg_price' in t for t in trend)
        # Should be sorted oldest first
        dates = [t['date'] for t in trend]
        assert dates == sorted(dates)
    
    def test_get_trend_no_data(self, test_db):
        """Test getting trend with no snapshots"""
        trend = get_price_trend("Honda", "Civic", days=7)
        
        assert trend == []


class TestTrendingCars:
    """Test trending cars functionality"""
    
    def test_trending_with_price_changes(self, test_db):
        """Test identifying trending cars"""
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        # Honda Civic - price went up
        test_db.add(DailySnapshot(
            date=week_ago, make="Honda", model="Civic",
            listing_count=10, avg_price=18000
        ))
        test_db.add(DailySnapshot(
            date=today, make="Honda", model="Civic",
            listing_count=12, avg_price=19500
        ))
        
        # Toyota Camry - price went down
        test_db.add(DailySnapshot(
            date=week_ago, make="Toyota", model="Camry",
            listing_count=8, avg_price=20000
        ))
        test_db.add(DailySnapshot(
            date=today, make="Toyota", model="Camry",
            listing_count=7, avg_price=18000
        ))
        test_db.commit()
        
        trending = get_trending_cars(days=7, limit=10)
        
        assert len(trending) == 2
        # Should be sorted by absolute change
        assert trending[0]['change'] != 0
        assert 'direction' in trending[0]
        assert trending[0]['direction'] in ['up', 'down']
    
    def test_trending_no_data(self, test_db):
        """Test trending cars with no data"""
        trending = get_trending_cars(days=7, limit=10)
        
        assert trending == []


class TestMarketOverview:
    """Test market overview functionality"""
    
    def test_overview_with_data(self, test_db):
        """Test market overview calculation"""
        today = date.today()
        
        # Add some snapshots
        for i in range(5):
            snapshot_date = today - timedelta(days=i)
            test_db.add(DailySnapshot(
                date=snapshot_date,
                make="Honda",
                model="Civic",
                listing_count=10,
                avg_price=18000
            ))
            test_db.add(DailySnapshot(
                date=snapshot_date,
                make="Toyota",
                model="Camry",
                listing_count=8,
                avg_price=20000
            ))
        test_db.commit()
        
        overview = get_market_overview(days=7)
        
        assert overview['total_unique_cars'] == 2
        assert overview['total_snapshots'] == 10
        assert overview['avg_market_price'] is not None
        assert 'most_listed' in overview
        assert len(overview['most_listed']) == 2
    
    def test_overview_empty_db(self, test_db):
        """Test overview with no data"""
        overview = get_market_overview(days=30)
        
        assert overview['total_unique_cars'] == 0
        assert overview['avg_market_price'] is None
        assert overview['most_listed'] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

