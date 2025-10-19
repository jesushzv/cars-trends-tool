"""
Tests for listing service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.listing_service import ListingService
from app.schemas.listing import ListingFilters
from app.models.listing import Listing


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def listing_service(mock_db):
    return ListingService(mock_db)


@pytest.mark.asyncio
async def test_get_listings_with_filters(listing_service, mock_db):
    """Test getting listings with filters"""
    # Mock database response
    mock_listing = Listing(
        id="test-id",
        platform="facebook",
        external_id="123",
        title="Test Car",
        make="Toyota",
        model="Camry",
        price=25000.00,
        views=100,
        likes=10,
        comments=5
    )
    
    mock_db.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_listing])))
    )
    
    filters = ListingFilters(
        platform="facebook",
        make="Toyota",
        days_back=30
    )
    
    result = await listing_service.get_listings(filters=filters)
    
    assert len(result) == 1
    assert result[0].platform == "facebook"
    assert result[0].make == "Toyota"


@pytest.mark.asyncio
async def test_get_top_listings_by_engagement(listing_service, mock_db):
    """Test getting top listings by engagement"""
    # Mock database response
    mock_listing = Listing(
        id="test-id",
        platform="facebook",
        external_id="123",
        title="Test Car",
        make="Toyota",
        model="Camry",
        price=25000.00,
        views=1000,
        likes=100,
        comments=50
    )
    
    mock_db.execute.return_value = MagicMock(
        scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[mock_listing])))
    )
    
    filters = ListingFilters(days_back=30)
    result = await listing_service.get_top_listings_by_engagement(limit=10, filters=filters)
    
    assert len(result) == 1
    assert result[0].views == 1000


@pytest.mark.asyncio
async def test_get_listings_summary(listing_service, mock_db):
    """Test getting listings summary"""
    # Mock database responses
    mock_db.execute.return_value = MagicMock(
        scalar=MagicMock(return_value=100),
        first=MagicMock(return_value=MagicMock(
            avg_price=25000.00,
            min_price=20000.00,
            max_price=30000.00,
            total_views=5000,
            total_likes=500,
            total_comments=100
        ))
    )
    
    filters = ListingFilters(days_back=30)
    result = await listing_service.get_listings_summary(filters)
    
    assert result.total_listings == 100
    assert result.total_views == 5000
    assert result.total_likes == 500
