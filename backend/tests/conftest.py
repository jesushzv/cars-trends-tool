"""
Pytest Configuration and Shared Fixtures
Phase: Test Suite Redesign - Critical import fix

This file configures the test environment and provides shared fixtures.
"""
import sys
import os
from pathlib import Path

# ============================================================================
# PATH CONFIGURATION - Fix import errors in CI
# ============================================================================

# Add parent directory (backend/) to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================

# Set test environment variables
os.environ.setdefault('USE_SQLITE_FALLBACK', 'true')
os.environ.setdefault('SECRET_KEY', 'test-secret-key-not-for-production-use-only')
os.environ.setdefault('ALGORITHM', 'HS256')
os.environ.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', '30')

# ============================================================================
# PYTEST FIXTURES
# ============================================================================

import pytest
from database import create_tables, SessionLocal


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create database tables once at the start of the test session.
    
    This runs automatically before any tests.
    Uses SQLite in-memory or fallback mode (configured via environment).
    """
    print("\n🔧 Setting up test database...")
    
    # Drop and recreate all tables to ensure fresh schema
    from database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    print("✅ Test database ready with fresh schema\n")
    yield
    print("\n🧹 Test session complete")


@pytest.fixture
def db_session():
    """
    Provide a database session for tests.
    
    Usage:
        def test_something(db_session):
            user = db_session.query(User).first()
            assert user is not None
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def clean_db(db_session):
    """
    Provide a clean database session with automatic rollback.
    
    This ensures each test starts with a fresh database state.
    
    Usage:
        def test_something(clean_db):
            # Test code here
            # Changes will be rolled back after test
    """
    yield db_session
    # Rollback any changes made during the test
    db_session.rollback()


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_listing_data():
    """
    Provide sample listing data for tests.
    
    Returns a dict with all required listing fields.
    """
    return {
        'platform': 'craigslist',
        'title': '2020 Honda Civic LX',
        'url': 'http://test.craigslist.com/car/123456.html',
        'price': 15000.0,
        'make': 'Honda',
        'model': 'Civic',
        'year': 2020,
        'mileage': 30000,
        'views': None,
        'likes': None,
        'comments': None
    }


@pytest.fixture
def sample_listings_batch():
    """
    Provide a batch of sample listings for bulk testing.
    
    Returns a list of listing dicts.
    """
    return [
        {
            'platform': 'craigslist',
            'title': '2020 Honda Civic',
            'url': 'http://test.com/1',
            'price': 15000,
            'make': 'Honda',
            'model': 'Civic',
            'year': 2020,
            'mileage': 30000
        },
        {
            'platform': 'mercadolibre',
            'title': '2019 Toyota Camry',
            'url': 'http://test.com/2',
            'price': 18000,
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2019,
            'mileage': 25000
        },
        {
            'platform': 'facebook',
            'title': '2021 Mazda3',
            'url': 'http://test.com/3',
            'price': 20000,
            'make': 'Mazda',
            'model': 'Mazda3',
            'year': 2021,
            'mileage': 15000
        }
    ]


# ============================================================================
# CONFIGURATION MARKERS
# ============================================================================

# Register custom pytest markers
def pytest_configure(config):
    """Register custom markers for test organization"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )

