"""
Tests for analytics service
Phase 8: Basic Analytics tests
"""
import pytest
from services.analytics_service import get_top_cars, get_top_makes, get_market_summary
from database import create_tables
from db_service import save_listing


class TestTopCars:
    """Test top cars analytics"""
    
    def test_get_top_cars_returns_list(self):
        """Test that get_top_cars returns a list"""
        result = get_top_cars(limit=10)
        assert isinstance(result, list)
    
    def test_get_top_cars_respects_limit(self):
        """Test that get_top_cars respects the limit parameter"""
        result = get_top_cars(limit=3)
        assert len(result) <= 3
    
    def test_top_cars_structure(self):
        """Test that each car has required fields"""
        result = get_top_cars(limit=1)
        if result:
            car = result[0]
            assert 'make' in car
            assert 'model' in car
            assert 'count' in car
            assert 'avg_price' in car
            assert 'min_price' in car
            assert 'max_price' in car
            assert isinstance(car['count'], int)
            assert car['count'] > 0
    
    def test_top_cars_sorted_by_count(self):
        """Test that cars are sorted by count descending"""
        result = get_top_cars(limit=10)
        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i]['count'] >= result[i+1]['count']
    
    def test_top_cars_no_nulls(self):
        """Test that results don't include cars with null make or model"""
        result = get_top_cars(limit=10)
        for car in result:
            assert car['make'] is not None
            assert car['model'] is not None


class TestTopMakes:
    """Test top makes analytics"""
    
    def test_get_top_makes_returns_list(self):
        """Test that get_top_makes returns a list"""
        result = get_top_makes(limit=5)
        assert isinstance(result, list)
    
    def test_get_top_makes_respects_limit(self):
        """Test that get_top_makes respects the limit parameter"""
        result = get_top_makes(limit=3)
        assert len(result) <= 3
    
    def test_top_makes_structure(self):
        """Test that each make has required fields"""
        result = get_top_makes(limit=1)
        if result:
            make = result[0]
            assert 'make' in make
            assert 'count' in make
            assert 'models_count' in make
            assert 'avg_price' in make
            assert isinstance(make['count'], int)
            assert make['count'] > 0
    
    def test_top_makes_sorted_by_count(self):
        """Test that makes are sorted by count descending"""
        result = get_top_makes(limit=5)
        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i]['count'] >= result[i+1]['count']


class TestMarketSummary:
    """Test market summary analytics"""
    
    def test_get_market_summary_returns_dict(self):
        """Test that get_market_summary returns a dict"""
        result = get_market_summary()
        assert isinstance(result, dict)
    
    def test_market_summary_structure(self):
        """Test that summary has required fields"""
        result = get_market_summary()
        assert 'total_listings' in result
        assert 'unique_makes' in result
        assert 'unique_models' in result
        assert 'avg_price' in result
        assert 'avg_year' in result
        assert 'avg_mileage' in result
    
    def test_market_summary_reasonable_values(self):
        """Test that summary values are reasonable"""
        result = get_market_summary()
        
        # Total listings should be non-negative
        assert result['total_listings'] >= 0
        
        # Unique makes/models should not exceed total listings
        assert result['unique_makes'] <= result['total_listings']
        assert result['unique_models'] <= result['total_listings']
        
        # If avg_year exists, it should be reasonable
        if result['avg_year']:
            assert 1990 <= result['avg_year'] <= 2026
        
        # If avg_price exists, it should be positive
        if result['avg_price']:
            assert result['avg_price'] > 0
        
        # If avg_mileage exists, it should be positive
        if result['avg_mileage']:
            assert result['avg_mileage'] > 0


class TestPlatformFiltering:
    """Test platform filtering in analytics"""
    
    def test_top_cars_with_platform_filter(self):
        """Test that platform filter works for top cars"""
        # Get all cars
        all_cars = get_top_cars(limit=50)
        
        # Get Craigslist only
        craigslist_cars = get_top_cars(limit=50, platform='craigslist')
        
        # Get Mercado Libre only
        mercadolibre_cars = get_top_cars(limit=50, platform='mercadolibre')
        
        # Results should be lists
        assert isinstance(craigslist_cars, list)
        assert isinstance(mercadolibre_cars, list)
        
        # Filtered results should not exceed all results
        assert len(craigslist_cars) <= len(all_cars)
        assert len(mercadolibre_cars) <= len(all_cars)
    
    def test_summary_with_platform_filter(self):
        """Test that platform filter works for summary"""
        # Get summaries for each platform
        all_summary = get_market_summary()
        craigslist_summary = get_market_summary(platform='craigslist')
        mercadolibre_summary = get_market_summary(platform='mercadolibre')
        
        # All should be dicts
        assert isinstance(all_summary, dict)
        assert isinstance(craigslist_summary, dict)
        assert isinstance(mercadolibre_summary, dict)
        
        # Filtered totals should not exceed overall total
        assert craigslist_summary['total_listings'] <= all_summary['total_listings']
        assert mercadolibre_summary['total_listings'] <= all_summary['total_listings']


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

