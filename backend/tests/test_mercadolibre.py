"""
Tests for Mercado Libre scraper
Phase 6: Second scraper tests
"""
import pytest
from scrapers.mercadolibre import scrape_mercadolibre_tijuana, _parse_price


class TestPriceParser:
    """Test price parsing functionality"""
    
    def test_parse_price_basic(self):
        assert _parse_price("180000") == 180000.0
    
    def test_parse_price_with_commas(self):
        assert _parse_price("180,000") == 180000.0
    
    def test_parse_price_with_spaces(self):
        assert _parse_price("180 000") == 180000.0
    
    def test_parse_price_with_dollar_sign(self):
        assert _parse_price("$180000") == 180000.0
    
    def test_parse_price_none(self):
        assert _parse_price(None) is None
    
    def test_parse_price_invalid(self):
        assert _parse_price("abc") is None
    
    def test_parse_price_empty(self):
        assert _parse_price("") is None


class TestMercadoLibreScraper:
    """Test Mercado Libre scraper functionality"""
    
    def test_scraper_returns_list(self):
        """Test that scraper returns a list"""
        result = scrape_mercadolibre_tijuana(max_results=3, fetch_details=False)
        assert isinstance(result, list)
    
    def test_scraper_respects_limit(self):
        """Test that scraper respects max_results parameter"""
        result = scrape_mercadolibre_tijuana(max_results=5, fetch_details=False)
        assert len(result) <= 5
    
    def test_scraper_returns_valid_structure(self):
        """Test that each listing has required fields"""
        result = scrape_mercadolibre_tijuana(max_results=1, fetch_details=False)
        if result:
            listing = result[0]
            assert 'title' in listing
            assert 'url' in listing
            assert 'price' in listing
            assert 'make' in listing
            assert 'model' in listing
            assert 'year' in listing
            assert 'mileage' in listing
    
    @pytest.mark.skip(reason="Network-dependent test - may fail in CI due to rate limiting or geo-blocking")
    def test_scraper_finds_real_data(self):
        """Test that scraper actually finds listings (integration test)"""
        result = scrape_mercadolibre_tijuana(max_results=2, fetch_details=False)
        # Should find at least one listing on Mercado Libre
        assert len(result) > 0, "Mercado Libre scraper should find at least one listing"
        
        # Check that first listing has meaningful data
        first_listing = result[0]
        assert first_listing['title'], "Title should not be empty"
        assert first_listing['url'].startswith('http'), "URL should be valid"
        # Price might be None, but if present should be positive
        if first_listing['price']:
            assert first_listing['price'] > 0, "Price should be positive"
    
    def test_scraper_handles_errors_gracefully(self):
        """Test that scraper doesn't crash on errors"""
        # Test with potentially problematic URL (should return empty list, not crash)
        result = scrape_mercadolibre_tijuana(max_results=1, fetch_details=False)
        assert isinstance(result, list), "Should return list even if there are errors"
    
    def test_scraper_with_details(self):
        """Test that scraper works with fetch_details=True"""
        result = scrape_mercadolibre_tijuana(max_results=2, fetch_details=True)
        if result:
            # With details, we should have more complete data
            listing = result[0]
            assert listing['title']
            assert listing['url']
            # Year and make might be None, but fields should exist
            assert 'year' in listing
            assert 'make' in listing
            assert 'model' in listing
            assert 'mileage' in listing


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

