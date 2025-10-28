"""
Tests for Facebook Marketplace scraper
Phase 11: Third data source with engagement metrics

NOTE: Most of these tests are unit tests that don't require actual Facebook access.
Integration tests requiring cookies are marked and skipped by default.
"""
import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.facebook_marketplace import (
    _load_cookies,
    _convert_cookies_to_playwright,
    _parse_price,
    _extract_engagement_metrics
)


class TestCookieLoading:
    """Test cookie loading functionality"""
    
    def test_load_cookies_file_not_found(self):
        """Test that _load_cookies returns None when file doesn't exist"""
        with patch('os.path.exists', return_value=False):
            result = _load_cookies()
            assert result is None
    
    def test_load_cookies_template_file(self, tmp_path):
        """Test that template file is detected and rejected"""
        # Create a temporary template file
        template_content = {
            "_comment": "This is a template",
            "_instructions": ["Step 1", "Step 2"],
            "c_user": "example"
        }
        
        cookie_file = tmp_path / "fb_cookies.json"
        with open(cookie_file, 'w') as f:
            json.dump(template_content, f)
        
        with patch('os.path.join', return_value=str(cookie_file)):
            result = _load_cookies()
            assert result is None
    
    def test_load_cookies_valid_file(self, tmp_path):
        """Test loading valid cookies"""
        valid_cookies = {
            "c_user": "123456789",
            "xs": "token123",
            "fr": "token456"
        }
        
        cookie_file = tmp_path / "fb_cookies.json"
        with open(cookie_file, 'w') as f:
            json.dump(valid_cookies, f)
        
        with patch('os.path.join', return_value=str(cookie_file)):
            result = _load_cookies()
            assert result is not None
            assert result["c_user"] == "123456789"
            assert result["xs"] == "token123"
    
    def test_load_cookies_invalid_json(self, tmp_path):
        """Test handling of invalid JSON"""
        cookie_file = tmp_path / "fb_cookies.json"
        with open(cookie_file, 'w') as f:
            f.write("{ invalid json }")
        
        with patch('os.path.join', return_value=str(cookie_file)):
            result = _load_cookies()
            assert result is None


class TestCookieConversion:
    """Test cookie format conversion for Playwright"""
    
    def test_convert_empty_cookies(self):
        """Test converting empty cookie dict"""
        result = _convert_cookies_to_playwright({})
        assert result == []
    
    def test_convert_single_cookie(self):
        """Test converting a single cookie"""
        cookies = {"c_user": "123456789"}
        result = _convert_cookies_to_playwright(cookies)
        
        assert len(result) == 1
        assert result[0]["name"] == "c_user"
        assert result[0]["value"] == "123456789"
        assert result[0]["domain"] == ".facebook.com"
        assert result[0]["path"] == "/"
        assert result[0]["httpOnly"] is True
        assert result[0]["secure"] is True
    
    def test_convert_multiple_cookies(self):
        """Test converting multiple cookies"""
        cookies = {
            "c_user": "123456789",
            "xs": "token123",
            "fr": "token456"
        }
        result = _convert_cookies_to_playwright(cookies)
        
        assert len(result) == 3
        cookie_names = [c["name"] for c in result]
        assert "c_user" in cookie_names
        assert "xs" in cookie_names
        assert "fr" in cookie_names
    
    def test_skip_underscore_fields(self):
        """Test that fields starting with _ are skipped"""
        cookies = {
            "_comment": "This should be skipped",
            "_instructions": "Also skipped",
            "c_user": "123456789"
        }
        result = _convert_cookies_to_playwright(cookies)
        
        assert len(result) == 1
        assert result[0]["name"] == "c_user"
    
    def test_convert_numeric_values(self):
        """Test that numeric cookie values are converted to strings"""
        cookies = {"c_user": 123456789}  # Numeric value
        result = _convert_cookies_to_playwright(cookies)
        
        assert len(result) == 1
        assert result[0]["value"] == "123456789"
        assert isinstance(result[0]["value"], str)


class TestPriceParser:
    """Test price parsing functionality"""
    
    def test_parse_simple_price(self):
        """Test parsing simple dollar amount"""
        assert _parse_price("$15000") == 15000.0
        assert _parse_price("$25000") == 25000.0
    
    def test_parse_price_with_commas(self):
        """Test parsing price with comma separators"""
        assert _parse_price("$15,000") == 15000.0
        assert _parse_price("$125,000") == 125000.0
        assert _parse_price("$1,250,000") == 1250000.0
    
    def test_parse_price_with_spaces(self):
        """Test parsing price with spaces"""
        assert _parse_price("$ 15 000") == 15000.0
        assert _parse_price("$15 000") == 15000.0
    
    def test_parse_price_mexican_format(self):
        """Test parsing Mexican peso format"""
        assert _parse_price("MX$180,000") == 180000.0
        assert _parse_price("MX$ 180000") == 180000.0
    
    def test_parse_price_none(self):
        """Test parsing None returns None"""
        assert _parse_price(None) is None
    
    def test_parse_price_invalid(self):
        """Test parsing invalid price returns None"""
        assert _parse_price("Not a price") is None
        assert _parse_price("abc") is None
    
    def test_parse_price_with_cents(self):
        """Test parsing price with cents (US format)"""
        assert _parse_price("$15,000.50") == 15000.5
        assert _parse_price("$125,000.99") == 125000.99
    
    def test_parse_price_mexican_period_separator(self):
        """Test parsing Mexican format with period as thousands separator"""
        # Mexican format uses period for thousands
        assert _parse_price("$40.000") == 40000.0
        assert _parse_price("$180.000") == 180000.0
        assert _parse_price("$1.250.000") == 1250000.0
        # This was the reported bug: 40.000 was being parsed as 40
        assert _parse_price("40.000") == 40000.0
        assert _parse_price("MX$40.000") == 40000.0
    
    def test_parse_price_mixed_separators(self):
        """Test edge cases with mixed separators"""
        # Period at end with 3 digits = thousands separator, not decimal
        assert _parse_price("$40.000") == 40000.0
        # Period with 2 digits at end = decimal point
        assert _parse_price("$40.50") == 40.5
        # Comma with period for cents
        assert _parse_price("$1,234.56") == 1234.56


class TestEngagementMetrics:
    """Test engagement metrics extraction (LIMITATION DOCUMENTED)
    
    As of 2025-10-26, Facebook Marketplace does NOT publicly display
    engagement metrics on listing pages. These tests verify that the
    function handles this limitation gracefully by returning None.
    """
    
    def test_extract_saves_metric(self):
        """Test that saves metric is NOT extracted (not publicly available)"""
        from bs4 import BeautifulSoup
        
        html = """
        <div>
            <span>25 people saved this</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        listing = {}
        
        _extract_engagement_metrics(soup, listing)
        
        # Facebook doesn't expose this data publicly
        assert listing.get('likes') is None
    
    def test_extract_views_metric(self):
        """Test that views metric is NOT extracted (not publicly available)"""
        from bs4 import BeautifulSoup
        
        html = """
        <div>
            <span>150 views</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        listing = {}
        
        _extract_engagement_metrics(soup, listing)
        
        # Facebook doesn't expose this data publicly
        assert listing.get('views') is None
    
    def test_extract_messages_metric(self):
        """Test that messages metric is NOT extracted (not publicly available)"""
        from bs4 import BeautifulSoup
        
        html = """
        <div>
            <span>10 people messaged about this</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        listing = {}
        
        _extract_engagement_metrics(soup, listing)
        
        # Facebook doesn't expose this data publicly
        assert listing.get('comments') is None
    
    def test_extract_multiple_metrics(self):
        """Test that NO metrics are extracted (not publicly available)"""
        from bs4 import BeautifulSoup
        
        html = """
        <div>
            <span>25 people saved this</span>
            <span>150 views</span>
            <span>10 people messaged</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        listing = {}
        
        _extract_engagement_metrics(soup, listing)
        
        # Facebook doesn't expose any engagement data publicly
        assert listing.get('likes') is None
        assert listing.get('views') is None
        assert listing.get('comments') is None
    
    def test_extract_no_metrics(self):
        """Test extraction when no metrics are present"""
        from bs4 import BeautifulSoup
        
        html = "<div><span>Some other text</span></div>"
        soup = BeautifulSoup(html, 'html.parser')
        listing = {}
        
        _extract_engagement_metrics(soup, listing)
        
        assert listing.get('likes') is None
        assert listing.get('views') is None
        assert listing.get('comments') is None


class TestScraperIntegration:
    """Integration tests for the scraper (require user setup)"""
    
    @pytest.mark.skip(reason="Requires valid Facebook cookies")
    def test_scrape_with_cookies(self):
        """Test actual scraping with cookies (skipped by default)"""
        from scrapers.facebook_marketplace import scrape_facebook_tijuana
        
        # This test would require actual cookies
        # Run manually if you have fb_cookies.json set up
        listings = scrape_facebook_tijuana(max_results=5, headless=True)
        
        assert isinstance(listings, list)
        # If cookies work, we should get at least some listings
        # (could be 0 if no listings available)
        
        if len(listings) > 0:
            # Verify listing structure
            listing = listings[0]
            assert 'url' in listing
            assert 'title' in listing or 'price' in listing
    
    def test_scrape_without_cookies(self):
        """Test scraping fails gracefully without cookies"""
        from scrapers.facebook_marketplace import scrape_facebook_tijuana
        
        # Ensure no cookies file exists for this test
        with patch('os.path.exists', return_value=False):
            listings = scrape_facebook_tijuana(max_results=5, headless=True)
            
            # Should return empty list, not crash
            assert listings == []


class TestAPIEndpoint:
    """Test the Facebook scraper API endpoint"""
    
    def test_api_endpoint_without_cookies(self):
        """Test API endpoint returns proper error without cookies"""
        from fastapi.testclient import TestClient
        import sys
        import os
        
        # Import the FastAPI app
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from main import app
        
        client = TestClient(app)
        
        with patch('os.path.exists', return_value=False):
            response = client.post("/scrape/facebook?max_results=5&save_to_db=false")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should indicate failure gracefully
            assert data["platform"] == "facebook"
            assert data["scraped"] == 0


# Run tests with: pytest tests/test_facebook_scraper.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

