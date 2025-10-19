"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.listing import Listing
from app.models.trend import Trend
from app.models.user import User
from app.models.scraping_session import ScrapingSession


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Create a test database session"""
    # Create in-memory SQLite database for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
async def sample_listing():
    """Create a sample listing for testing"""
    return Listing(
        platform="facebook",
        external_id="test-123",
        title="2019 Toyota Camry LE",
        description="Excellent condition, low mileage",
        make="Toyota",
        model="Camry",
        year=2019,
        price=25000.00,
        currency="MXN",
        condition="used",
        mileage=45000,
        location="Tijuana, Mexico",
        url="https://example.com/listing",
        views=100,
        likes=10,
        comments=5,
        saves=2,
        shares=1
    )


@pytest.fixture
async def sample_trend():
    """Create a sample trend for testing"""
    return Trend(
        make="Toyota",
        model="Camry",
        date="2023-01-01",
        total_listings=10,
        avg_price=25000.00,
        min_price=20000.00,
        max_price=30000.00,
        total_views=1000,
        total_likes=100,
        total_comments=50,
        total_saves=20,
        total_shares=10,
        engagement_score=1500.0
    )


@pytest.fixture
async def sample_user():
    """Create a sample user for testing"""
    return User(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8K5K5K.",
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )


@pytest.fixture
async def sample_scraping_session():
    """Create a sample scraping session for testing"""
    return ScrapingSession(
        platform="facebook",
        status="completed",
        listings_found=100,
        listings_processed=95,
        listings_new=20,
        listings_updated=75,
        execution_time_seconds=300
    )
