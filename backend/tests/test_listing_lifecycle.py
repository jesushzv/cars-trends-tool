"""
Tests for Listing Lifecycle Service
Sub-Phase 2.2: Service Layer Tests

Tests the lifecycle tracking functionality for listings:
- Creating new listings
- Updating existing listings
- Price change tracking
- Active/inactive listing queries
"""
import pytest
from datetime import datetime, timedelta
from services.listing_lifecycle_service import (
    upsert_listing,
    get_active_listings,
    get_inactive_listings,
    get_listing_stats
)
from models import Listing
from database import SessionLocal


class TestUpsertListing:
    """Test upsert_listing functionality"""
    
    def test_create_new_listing(self, setup_test_database):
        """Test creating a new listing"""
        listing_data = {
            'platform': 'test',
            'title': 'Test Car 2020',
            'url': 'http://test.com/car/new_listing_001',
            'price': 15000.0,
            'make': 'Honda',
            'model': 'Civic',
            'year': 2020,
            'mileage': 50000
        }
        
        result = upsert_listing(listing_data)
        
        assert result.id is not None
        assert result.url == listing_data['url']
        assert result.price == 15000.0
        assert result.first_seen is not None
        assert result.last_seen is not None
        assert result.first_seen == result.last_seen  # Should be same for new listing
    
    def test_update_existing_listing(self, setup_test_database):
        """Test updating an existing listing"""
        listing_data = {
            'platform': 'test',
            'title': 'Test Car 2020',
            'url': 'http://test.com/car/update_test_001',
            'price': 15000.0,
            'make': 'Honda',
            'model': 'Civic',
            'year': 2020,
            'mileage': 50000
        }
        
        # Create initial listing
        first = upsert_listing(listing_data)
        first_seen_time = first.first_seen
        
        # Update the same listing
        import time
        time.sleep(0.1)  # Small delay to ensure different timestamp
        listing_data['price'] = 14500.0  # Price change
        
        second = upsert_listing(listing_data)
        
        # Should be same listing (same ID)
        assert second.id == first.id
        # First seen should not change
        assert second.first_seen == first_seen_time
        # Last seen should be updated
        assert second.last_seen > first.last_seen
        # Price should be updated
        assert second.price == 14500.0
    
    def test_upsert_without_url_raises_error(self, setup_test_database):
        """Test that upsert raises ValueError without URL"""
        listing_data = {
            'platform': 'test',
            'title': 'Test Car 2020',
            'price': 15000.0,
        }
        # Missing 'url' key
        
        with pytest.raises(ValueError, match="URL is required"):
            upsert_listing(listing_data)
    
    def test_upsert_updates_title(self, setup_test_database):
        """Test that upsert updates title if changed"""
        listing_data = {
            'platform': 'test',
            'title': 'Original Title',
            'url': 'http://test.com/car/title_test_001',
            'price': 15000.0,
        }
        
        first = upsert_listing(listing_data)
        assert first.title == 'Original Title'
        
        # Update with new title
        listing_data['title'] = 'Updated Title'
        second = upsert_listing(listing_data)
        
        assert second.id == first.id
        assert second.title == 'Updated Title'
    
    def test_upsert_updates_engagement_metrics(self, setup_test_database):
        """Test that upsert updates engagement metrics"""
        listing_data = {
            'platform': 'facebook',
            'title': 'Test Car',
            'url': 'http://test.com/car/engagement_test_001',
            'price': 15000.0,
            'views': 100,
            'likes': 10,
            'comments': 2
        }
        
        first = upsert_listing(listing_data)
        assert first.views == 100
        assert first.likes == 10
        assert first.comments == 2
        
        # Update engagement
        listing_data['views'] = 150
        listing_data['likes'] = 15
        listing_data['comments'] = 5
        
        second = upsert_listing(listing_data)
        
        assert second.id == first.id
        assert second.views == 150
        assert second.likes == 15
        assert second.comments == 5
    
    def test_upsert_with_none_price(self, setup_test_database):
        """Test upserting listing with None price"""
        listing_data = {
            'platform': 'test',
            'title': 'Test Car',
            'url': 'http://test.com/car/no_price_001',
            'price': None,  # Price not available
        }
        
        result = upsert_listing(listing_data)
        
        assert result.id is not None
        assert result.price is None


class TestActiveInactiveListings:
    """Test active/inactive listing queries"""
    
    def test_get_active_listings(self, setup_test_database):
        """Test retrieving active listings"""
        db = SessionLocal()
        
        # Create a recent listing (active)
        recent = Listing(
            platform='test',
            title='Recent Car',
            url='http://test.com/recent',
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            scraped_at=datetime.utcnow()
        )
        db.add(recent)
        
        # Create an old listing (inactive)
        old = Listing(
            platform='test',
            title='Old Car',
            url='http://test.com/old',
            first_seen=datetime.utcnow() - timedelta(days=30),
            last_seen=datetime.utcnow() - timedelta(days=10),
            scraped_at=datetime.utcnow() - timedelta(days=10)
        )
        db.add(old)
        
        db.commit()
        db.close()
        
        # Get active listings (last 7 days)
        active = get_active_listings(days_old=7)
        
        active_urls = [listing.url for listing in active]
        assert 'http://test.com/recent' in active_urls
        assert 'http://test.com/old' not in active_urls
    
    def test_get_inactive_listings(self, setup_test_database):
        """Test retrieving inactive listings"""
        db = SessionLocal()
        
        # Create a recent listing (active)
        recent = Listing(
            platform='test',
            title='Recent Car',
            url='http://test.com/inactive_test_recent',
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
            scraped_at=datetime.utcnow()
        )
        db.add(recent)
        
        # Create an old listing (inactive)
        old = Listing(
            platform='test',
            title='Old Car',
            url='http://test.com/inactive_test_old',
            first_seen=datetime.utcnow() - timedelta(days=30),
            last_seen=datetime.utcnow() - timedelta(days=10),
            scraped_at=datetime.utcnow() - timedelta(days=10)
        )
        db.add(old)
        
        db.commit()
        db.close()
        
        # Get inactive listings (older than 7 days)
        inactive = get_inactive_listings(days_old=7)
        
        inactive_urls = [listing.url for listing in inactive]
        assert 'http://test.com/inactive_test_recent' not in inactive_urls
        assert 'http://test.com/inactive_test_old' in inactive_urls
    
    def test_active_listings_with_different_timeframe(self, setup_test_database):
        """Test active listings with custom timeframe"""
        db = SessionLocal()
        
        # Create listing from 5 days ago
        five_days_old = Listing(
            platform='test',
            title='Five Day Old Car',
            url='http://test.com/five_days',
            first_seen=datetime.utcnow() - timedelta(days=5),
            last_seen=datetime.utcnow() - timedelta(days=5),
            scraped_at=datetime.utcnow() - timedelta(days=5)
        )
        db.add(five_days_old)
        db.commit()
        db.close()
        
        # Should be active with 7-day window
        active_7 = get_active_listings(days_old=7)
        urls_7 = [l.url for l in active_7]
        assert 'http://test.com/five_days' in urls_7
        
        # Should be inactive with 3-day window
        active_3 = get_active_listings(days_old=3)
        urls_3 = [l.url for l in active_3]
        assert 'http://test.com/five_days' not in urls_3


class TestListingStats:
    """Test listing statistics"""
    
    def test_get_listing_stats_empty_db(self, setup_test_database):
        """Test getting stats from empty database"""
        # Clear all listings first
        db = SessionLocal()
        db.query(Listing).delete()
        db.commit()
        db.close()
        
        stats = get_listing_stats()
        
        assert stats['total_listings'] == 0
        assert stats['active_last_7_days'] == 0
        assert stats['inactive_7_days'] == 0
    
    def test_get_listing_stats_with_data(self, setup_test_database):
        """Test getting stats with listings"""
        db = SessionLocal()
        
        # Create mix of active and inactive
        for i in range(5):
            active = Listing(
                platform='test',
                title=f'Active Car {i}',
                url=f'http://test.com/stats_active_{i}',
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                scraped_at=datetime.utcnow()
            )
            db.add(active)
        
        for i in range(3):
            inactive = Listing(
                platform='test',
                title=f'Inactive Car {i}',
                url=f'http://test.com/stats_inactive_{i}',
                first_seen=datetime.utcnow() - timedelta(days=20),
                last_seen=datetime.utcnow() - timedelta(days=10),
                scraped_at=datetime.utcnow() - timedelta(days=10)
            )
            db.add(inactive)
        
        db.commit()
        db.close()
        
        stats = get_listing_stats()
        
        # Should have 8+ total (including any from other tests)
        assert stats['total_listings'] >= 8
        # Should have 5+ active
        assert stats['active_last_7_days'] >= 5
        # Should have 3+ inactive
        assert stats['inactive_7_days'] >= 3
        # Average days should be calculated
        assert 'average_days_active' in stats


class TestPriceChangeTracking:
    """Test price change detection and logging"""
    
    def test_price_change_is_tracked(self, setup_test_database):
        """Test that price changes are properly tracked"""
        listing_data = {
            'platform': 'test',
            'title': 'Price Change Test',
            'url': 'http://test.com/car/price_change_001',
            'price': 20000.0,
        }
        
        # Create initial
        first = upsert_listing(listing_data)
        assert first.price == 20000.0
        
        # Update with new price
        listing_data['price'] = 18000.0
        second = upsert_listing(listing_data)
        
        assert second.id == first.id
        assert second.price == 18000.0
    
    def test_price_null_to_value(self, setup_test_database):
        """Test updating from null price to actual price"""
        listing_data = {
            'platform': 'test',
            'title': 'Price Update Test',
            'url': 'http://test.com/car/price_null_001',
            'price': None,
        }
        
        first = upsert_listing(listing_data)
        assert first.price is None
        
        # Add price later
        listing_data['price'] = 15000.0
        second = upsert_listing(listing_data)
        
        assert second.id == first.id
        assert second.price == 15000.0
    
    def test_no_price_change_when_same(self, setup_test_database):
        """Test that same price doesn't trigger update"""
        listing_data = {
            'platform': 'test',
            'title': 'Same Price Test',
            'url': 'http://test.com/car/same_price_001',
            'price': 15000.0,
        }
        
        first = upsert_listing(listing_data)
        original_price = first.price
        
        # "Update" with same price
        second = upsert_listing(listing_data)
        
        assert second.id == first.id
        assert second.price == original_price
        assert second.price == 15000.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

