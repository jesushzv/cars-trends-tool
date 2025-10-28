"""
Database configuration and session management
Phase 2: SQLite database setup
Phase 17: PostgreSQL support added
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database configuration
# Priority: Environment variable > PostgreSQL (if available) > SQLite (fallback)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://carstrends:carstrends@localhost:5432/carstrends"
)

# Fallback to SQLite if PostgreSQL is not available
USE_SQLITE_FALLBACK = os.getenv("USE_SQLITE_FALLBACK", "false").lower() == "true"
if USE_SQLITE_FALLBACK:
    DATABASE_URL = "sqlite:///./listings.db"

# Create database engine
# Configure based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,  # Connection pool size
        max_overflow=10,  # Max connections beyond pool_size
        echo=False  # Set to True for SQL debugging
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session
    Usage in FastAPI: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables in the database
    This should be called once during app initialization
    """
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


if __name__ == "__main__":
    # Test database connection and table creation
    print("Testing database connection...")
    print(f"Database URL: {DATABASE_URL}")
    print(f"Engine: {engine}")
    print("✓ Database engine created successfully")
    
    print("\nCreating tables...")
    # Import models to register them with Base
    from models import Listing  # noqa: F401
    create_tables()
    print("✓ All tables created")

