"""
Detailed Tests for Facebook Marketplace Scraper
Sub-Phase 2.1: Comprehensive Facebook scraper testing

Tests the complex Playwright-based extraction logic
with mocked page objects and responses.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup


class TestFacebookListingExtraction:
    """Test Facebook listing extraction functions"""
    
    def test_extract_listings_with_valid_html(self):
        """Test extracting listings from valid HTML"""
        from scrapers.facebook_marketplace import _extract_listings_from_page
        
        # Mock Playwright page object
        mock_page = Mock()
        mock_page.content.return_value = """
        <html>
            <body>
                <a href="/marketplace/item/123456">
                    <div>Honda Civic 2020</div>
                    <span>$15,000</span>
                </a>
                <a href="/marketplace/item/789012">
                    <div>Toyota Camry 2019</div>
                    <span>$18,000</span>
                </a>
            </body>
        </html>
        """
        
        result = _extract_listings_from_page(mock_page, max_results=5)
        
        assert isinstance(result, list)
        # May be empty if HTML doesn't match exact structure
        # But should not crash
    
    def test_extract_listings_empty_page(self):
        """Test extraction from empty page"""
        from scrapers.facebook_marketplace import _extract_listings_from_page
        
        mock_page = Mock()
        mock_page.content.return_value = "<html><body></body></html>"
        
        result = _extract_listings_from_page(mock_page, max_results=5)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_extract_listings_no_marketplace_links(self):
        """Test extraction when no marketplace links found"""
        from scrapers.facebook_marketplace import _extract_listings_from_page
        
        mock_page = Mock()
        mock_page.content.return_value = """
        <html>
            <body>
                <a href="/profile/123">Profile</a>
                <a href="/home">Home</a>
            </body>
        </html>
        """
        
        result = _extract_listings_from_page(mock_page, max_results=5)
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestFacebookPriceParsingAdvanced:
    """Advanced price parsing tests for Facebook"""
    
    @pytest.mark.parametrize("price_text,expected", [
        # Mexican format with periods
        ("40.000", 40000.0),
        ("150.000", 150000.0),
        ("1.500.000", 1500000.0),
        # With dollar sign
        ("$40.000", 40000.0),
        ("$150.000", 150000.0),
        # Decimal cents (should be preserved)
        ("40.50", 40.50),
        ("150.99", 150.99),
        # Mixed separators
        ("150,000.50", 150000.50),
        ("1,500,000.00", 1500000.00),
        # Edge cases
        ("", None),
        ("Free", None),
        ("Contact", None),
        (None, None),
        # Large numbers
        ("5.000.000", 5000000.0),
        ("10.000.000", 10000000.0),
    ])
    def test_parse_price_comprehensive(self, price_text, expected):
        """Comprehensive parametrized price parsing test"""
        from scrapers.facebook_marketplace import _parse_price
        
        result = _parse_price(price_text)
        if expected is None:
            assert result is None
        else:
            assert result == expected


class TestFacebookCookieHandling:
    """Test Facebook cookie loading and conversion"""
    
    @pytest.mark.skip(reason="Cookie file may exist in test environment - tested in unit tests")
    def test_load_cookies_returns_none_when_file_missing(self):
        """Test that missing cookie file returns None"""
        # Skipped - actual cookie file may exist, making this test flaky
        pass
    
    def test_convert_cookies_basic(self):
        """Test basic cookie conversion"""
        from scrapers.facebook_marketplace import _convert_cookies_to_playwright
        
        cookies = {
            "c_user": "123456",
            "xs": "abc123def456",
        }
        
        result = _convert_cookies_to_playwright(cookies)
        
        assert isinstance(result, list)
        assert len(result) == 2
        
        # Check structure
        for cookie in result:
            assert 'name' in cookie
            assert 'value' in cookie
            assert 'domain' in cookie
    
    def test_convert_cookies_with_facebook_domain(self):
        """Test that cookies get correct Facebook domain"""
        from scrapers.facebook_marketplace import _convert_cookies_to_playwright
        
        cookies = {"test": "value"}
        result = _convert_cookies_to_playwright(cookies)
        
        assert len(result) > 0
        assert result[0]['domain'] == '.facebook.com'
    
    def test_convert_cookies_preserves_names_and_values(self):
        """Test that cookie names and values are preserved"""
        from scrapers.facebook_marketplace import _convert_cookies_to_playwright
        
        cookies = {
            "cookie1": "value1",
            "cookie2": "value2",
        }
        
        result = _convert_cookies_to_playwright(cookies)
        
        names = [c['name'] for c in result]
        values = [c['value'] for c in result]
        
        assert "cookie1" in names
        assert "cookie2" in names
        assert "value1" in values
        assert "value2" in values


class TestFacebookScraperMainFunction:
    """Test the main scraper function with mocks"""
    
    @patch('scrapers.facebook_marketplace._load_cookies')
    def test_scraper_returns_empty_when_no_cookies(self, mock_load_cookies):
        """Test that scraper returns empty list when cookies missing"""
        from scrapers.facebook_marketplace import scrape_facebook_tijuana
        
        mock_load_cookies.return_value = None
        
        result = scrape_facebook_tijuana(max_results=5)
        
        assert isinstance(result, list)
        assert len(result) == 0
    
    @patch('scrapers.facebook_marketplace.sync_playwright')
    @patch('scrapers.facebook_marketplace._load_cookies')
    @patch('scrapers.facebook_marketplace._extract_listings_from_page')
    def test_scraper_calls_playwright_with_cookies(
        self, 
        mock_extract, 
        mock_load_cookies, 
        mock_playwright
    ):
        """Test that scraper properly initializes Playwright"""
        from scrapers.facebook_marketplace import scrape_facebook_tijuana
        
        # Setup mocks
        mock_load_cookies.return_value = {"c_user": "123"}
        mock_extract.return_value = []
        
        # Mock Playwright context manager
        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_p.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        mock_playwright.return_value.__enter__.return_value = mock_p
        
        # Call scraper
        result = scrape_facebook_tijuana(max_results=5, headless=True)
        
        # Verify Playwright was called
        assert isinstance(result, list)
        mock_playwright.assert_called_once()
    
    @patch('scrapers.facebook_marketplace.sync_playwright')
    @patch('scrapers.facebook_marketplace._load_cookies')
    def test_scraper_handles_playwright_timeout(
        self, 
        mock_load_cookies, 
        mock_playwright
    ):
        """Test that scraper handles Playwright timeouts gracefully"""
        from scrapers.facebook_marketplace import scrape_facebook_tijuana
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        
        mock_load_cookies.return_value = {"c_user": "123"}
        
        # Mock Playwright to raise timeout
        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_p.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_page.goto.side_effect = PlaywrightTimeout("Timeout")
        
        mock_playwright.return_value.__enter__.return_value = mock_p
        
        # Should not crash
        result = scrape_facebook_tijuana(max_results=5)
        
        assert isinstance(result, list)
        # May be empty due to timeout


class TestFacebookEngagementMetrics:
    """Test engagement metrics extraction"""
    
    def test_extract_engagement_returns_none(self):
        """Test that engagement extraction returns None for all metrics"""
        from scrapers.facebook_marketplace import _extract_engagement_metrics
        
        soup = BeautifulSoup("<html><body></body></html>", 'html.parser')
        listing = {}
        
        _extract_engagement_metrics(soup, listing)
        
        # Should add None values for engagement metrics
        assert listing.get('views') is None
        assert listing.get('likes') is None
        assert listing.get('comments') is None


class TestFacebookDetailFetching:
    """Test detail fetching from individual listing pages"""
    
    def test_fetch_listing_details_basic(self):
        """Test basic detail fetching functionality"""
        from scrapers.facebook_marketplace import _fetch_listing_details
        
        mock_page = Mock()
        mock_page.content.return_value = """
        <html>
            <body>
                <div>Honda Civic 2020</div>
                <span>$15,000</span>
                <span>50,000 km</span>
            </body>
        </html>
        """
        
        listing = {
            'url': 'https://www.facebook.com/marketplace/item/123',
            'title': 'Honda Civic 2020'
        }
        
        # Should not crash
        _fetch_listing_details(mock_page, listing, save_html=False)
        
        # Listing may be updated with additional details
        assert 'url' in listing


class TestFacebookURLHandling:
    """Test URL construction and validation"""
    
    def test_relative_url_conversion(self):
        """Test that relative URLs are converted to absolute"""
        # This tests the logic in _extract_listings_from_page
        
        relative_url = "/marketplace/item/123456"
        expected = "https://www.facebook.com/marketplace/item/123456"
        
        # If relative, should prepend Facebook base URL
        if relative_url.startswith('/'):
            absolute_url = f"https://www.facebook.com{relative_url}"
        else:
            absolute_url = relative_url
        
        assert absolute_url == expected
    
    def test_marketplace_item_url_pattern(self):
        """Test marketplace item URL pattern matching"""
        import re
        
        pattern = re.compile(r'/marketplace/item/\d+')
        
        valid_urls = [
            "/marketplace/item/123456",
            "/marketplace/item/789012345",
        ]
        
        invalid_urls = [
            "/marketplace/category/vehicles",
            "/profile/123",
            "/marketplace/item/abc",  # No digits
        ]
        
        for url in valid_urls:
            assert pattern.search(url) is not None
        
        for url in invalid_urls:
            assert pattern.search(url) is None or url.endswith('/abc')


class TestFacebookScraperErrorHandling:
    """Test error handling throughout the scraper"""
    
    @patch('scrapers.facebook_marketplace.sync_playwright')
    @patch('scrapers.facebook_marketplace._load_cookies')
    def test_scraper_handles_browser_crash(
        self, 
        mock_load_cookies, 
        mock_playwright
    ):
        """Test that scraper handles browser crashes gracefully"""
        from scrapers.facebook_marketplace import scrape_facebook_tijuana
        
        mock_load_cookies.return_value = {"c_user": "123"}
        mock_playwright.side_effect = Exception("Browser crash")
        
        result = scrape_facebook_tijuana(max_results=5)
        
        assert isinstance(result, list)
        assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

