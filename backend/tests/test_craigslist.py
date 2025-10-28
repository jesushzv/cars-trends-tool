"""
Phase 1 Tests - Craigslist Scraper
"""
import pytest
from scrapers.craigslist import scrape_craigslist_tijuana, _parse_price


class TestPriceParser:
    """Test the price parsing utility function"""
    
    def test_parse_price_with_dollar_sign(self):
        """Should parse '$12,000' to 12000.0"""
        assert _parse_price('$12,000') == 12000.0
    
    def test_parse_price_without_dollar_sign(self):
        """Should parse '15000' to 15000.0"""
        assert _parse_price('15000') == 15000.0
    
    def test_parse_price_with_commas(self):
        """Should parse '1,234,567' to 1234567.0"""
        assert _parse_price('1,234,567') == 1234567.0
    
    def test_parse_price_with_whitespace(self):
        """Should handle whitespace"""
        assert _parse_price('  $10,000  ') == 10000.0
    
    def test_parse_price_none(self):
        """Should return None for None input"""
        assert _parse_price(None) is None
    
    def test_parse_price_invalid(self):
        """Should return None for invalid price"""
        assert _parse_price('not a price') is None
        assert _parse_price('') is None


class TestCraigslistScraper:
    """Test the main Craigslist scraper function"""
    
    def test_scraper_returns_list(self):
        """Scraper should return a list"""
        result = scrape_craigslist_tijuana(max_results=5)
        assert isinstance(result, list)
    
    def test_scraper_respects_limit(self):
        """Scraper should respect max_results parameter"""
        result = scrape_craigslist_tijuana(max_results=3)
        assert len(result) <= 3
    
    def test_scraper_returns_valid_structure(self):
        """Each listing should have title, price, url"""
        result = scrape_craigslist_tijuana(max_results=5)
        
        if len(result) > 0:
            # Check first listing has required fields
            listing = result[0]
            assert 'title' in listing
            assert 'url' in listing
            assert 'price' in listing
            
            # Check types
            assert isinstance(listing['title'], str)
            assert isinstance(listing['url'], str)
            assert listing['title'] != ''
            assert listing['url'].startswith('http')
    
    @pytest.mark.skip(reason="Network-dependent test - may fail in CI due to rate limiting or geo-blocking")
    def test_scraper_finds_real_data(self):
        """Scraper should return at least some listings from real Craigslist"""
        result = scrape_craigslist_tijuana(max_results=10)
        # We expect at least 1 listing from Tijuana Craigslist
        assert len(result) > 0, "Should find at least 1 car listing"
    
    def test_scraper_handles_errors_gracefully(self):
        """Scraper should not crash on errors"""
        try:
            result = scrape_craigslist_tijuana(max_results=5)
            assert isinstance(result, list)
        except Exception as e:
            pytest.fail(f"Scraper should not raise exceptions: {e}")

