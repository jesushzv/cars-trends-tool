"""
Scraping session model for tracking scraping operations
"""

from sqlalchemy import Column, String, Integer, DateTime, ARRAY, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class ScrapingSession(Base):
    """Scraping session model for tracking scraping operations"""
    
    __tablename__ = "scraping_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(String(20), nullable=False, index=True)
    started_at = Column(DateTime, default=func.now(), index=True)
    completed_at = Column(DateTime, index=True)
    status = Column(String(20), default="running", index=True)
    listings_found = Column(Integer, default=0)
    listings_processed = Column(Integer, default=0)
    listings_new = Column(Integer, default=0)
    listings_updated = Column(Integer, default=0)
    errors = Column(ARRAY(String))
    execution_time_seconds = Column(Integer)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("platform IN ('facebook', 'craigslist', 'mercadolibre')", name="check_platform"),
        CheckConstraint("status IN ('running', 'completed', 'failed', 'cancelled')", name="check_status"),
        CheckConstraint("listings_found >= 0", name="check_listings_found"),
        CheckConstraint("listings_processed >= 0", name="check_listings_processed"),
        CheckConstraint("listings_new >= 0", name="check_listings_new"),
        CheckConstraint("listings_updated >= 0", name="check_listings_updated"),
        CheckConstraint("execution_time_seconds >= 0", name="check_execution_time"),
        CheckConstraint("listings_processed <= listings_found", name="check_processed_vs_found"),
        CheckConstraint(
            "(status = 'running' AND completed_at IS NULL) OR (status IN ('completed', 'failed', 'cancelled') AND completed_at IS NOT NULL)",
            name="check_completion_status"
        ),
        {"extend_existing": True}
    )
    
    def __repr__(self):
        return f"<ScrapingSession(id={self.id}, platform={self.platform}, status={self.status})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "platform": self.platform,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "listings_found": self.listings_found,
            "listings_processed": self.listings_processed,
            "listings_new": self.listings_new,
            "listings_updated": self.listings_updated,
            "errors": self.errors or [],
            "execution_time_seconds": self.execution_time_seconds
        }
