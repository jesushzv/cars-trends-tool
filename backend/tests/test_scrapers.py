"""
Tests for scrapers
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.scrapers.facebook_marketplace import FacebookMarketplaceScraper
from app.scrapers.craigslist import CraigslistScraper
from app.scrapers.mercadolibre import MercadoLibreScraper


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def facebook_scraper(mock_db):
    return FacebookMarketplaceScraper(mock_db)


@pytest.fixture
def craigslist_scraper(mock_db):
    return CraigslistScraper(mock_db)


@pytest.fixture
def mercadolibre_scraper(mock_db):
    return MercadoLibreScraper(mock_db)


@pytest.mark.asyncio
async def test_facebook_scraper_extract_car_info(facebook_scraper):
    """Test Facebook scraper car info extraction"""
    # Test the utility methods directly
    full_text = "2019 Toyota Camry LE Low mileage, excellent condition, 45,000 miles"
    
    make, model = facebook_scraper._extract_make_model(full_text)
    year = facebook_scraper.extract_year(full_text)
    mileage = facebook_scraper.clean_mileage("45,000 miles")
    
    assert make == 'toyota'
    assert model == 'camry'
    assert year == 2019
    assert mileage == 45000


@pytest.mark.asyncio
async def test_craigslist_scraper_extract_car_info(craigslist_scraper):
    """Test Craigslist scraper car info extraction"""
    from bs4 import BeautifulSoup
    
    html = """
    <html>
        <span id="titletextonly">2020 Honda Civic</span>
        <section id="postingbody">Great car, 30,000 miles, excellent condition</section>
        <span class="price">$22,000</span>
    </html>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    title = craigslist_scraper._extract_title(soup)
    description = craigslist_scraper._extract_description(soup)
    price = craigslist_scraper._extract_price(soup)
    
    assert title == "2020 Honda Civic"
    assert "Great car" in description
    assert price == 22000.0


@pytest.mark.asyncio
async def test_mercadolibre_scraper_extract_car_info(mercadolibre_scraper):
    """Test Mercado Libre scraper car info extraction"""
    from bs4 import BeautifulSoup
    
    html = """
    <html>
        <h1 class="ui-pdp-title">Nissan Sentra 2018</h1>
        <p class="ui-pdp-description__content">Auto en excelente estado, 25,000 km</p>
        <span class="andes-money-amount__fraction">180000</span>
    </html>
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    title = mercadolibre_scraper._extract_title(soup)
    description = mercadolibre_scraper._extract_description(soup)
    price = mercadolibre_scraper._extract_price(soup)
    
    assert title == "Nissan Sentra 2018"
    assert "excelente estado" in description
    assert price == 180000.0


@pytest.mark.asyncio
async def test_base_scraper_normalize_car_model():
    """Test base scraper car model normalization"""
    from app.scrapers.base_scraper import BaseScraper
    
    scraper = FacebookMarketplaceScraper(AsyncMock())
    
    # Test normalization
    make, model = scraper.normalize_car_model("Chevrolet", "Silverado")
    assert make == "chevy"
    assert model == "silverado"
    
    make, model = scraper.normalize_car_model("Mercedes-Benz", "C-Class")
    assert make == "mercedes"
    assert model == "c-class"


@pytest.mark.asyncio
async def test_base_scraper_clean_price():
    """Test base scraper price cleaning"""
    from app.scrapers.base_scraper import BaseScraper
    
    scraper = FacebookMarketplaceScraper(AsyncMock())
    
    # Test price cleaning
    assert scraper.clean_price("$25,000") == 25000.0
    assert scraper.clean_price("25,000.50") == 25000.5
    assert scraper.clean_price("Invalid price") is None
    assert scraper.clean_price("") is None


@pytest.mark.asyncio
async def test_base_scraper_clean_mileage():
    """Test base scraper mileage cleaning"""
    from app.scrapers.base_scraper import BaseScraper
    
    scraper = FacebookMarketplaceScraper(AsyncMock())
    
    # Test mileage cleaning
    assert scraper.clean_mileage("50,000") == 50000
    assert scraper.clean_mileage("50000") == 50000
    assert scraper.clean_mileage("Invalid mileage") is None
    assert scraper.clean_mileage("") is None


@pytest.mark.asyncio
async def test_base_scraper_extract_year():
    """Test base scraper year extraction"""
    from app.scrapers.base_scraper import BaseScraper
    
    scraper = FacebookMarketplaceScraper(AsyncMock())
    
    # Test year extraction
    assert scraper.extract_year("2019 Toyota Camry") == 2019
    assert scraper.extract_year("Model year 2020") == 2020
    assert scraper.extract_year("No year here") is None
    assert scraper.extract_year("") is None
