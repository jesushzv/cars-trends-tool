"""
Listing model for car listings from all platforms
"""

from sqlalchemy import Column, String, Integer, DECIMAL, Boolean, DateTime, Text, ARRAY, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class Listing(Base):
    """Car listing model"""
    
    __tablename__ = "listings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(String(20), nullable=False, index=True)
    external_id = Column(String(100), nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    make = Column(String(50), index=True)
    model = Column(String(50), index=True)
    year = Column(Integer)
    price = Column(DECIMAL(12, 2))
    currency = Column(String(3), default="MXN")
    condition = Column(String(20))
    mileage = Column(Integer)
    location = Column(String(100))
    url = Column(Text, nullable=False)
    images = Column(ARRAY(Text))
    
    # Engagement metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    # Metadata
    posted_date = Column(DateTime)
    scraped_at = Column(DateTime, default=func.now(), index=True)
    is_active = Column(Boolean, default=True, index=True)
    is_duplicate = Column(Boolean, default=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("platform IN ('facebook', 'craigslist', 'mercadolibre')", name="check_platform"),
        CheckConstraint("year >= 1900 AND year <= EXTRACT(YEAR FROM NOW()) + 1", name="check_year"),
        CheckConstraint("price >= 0", name="check_price"),
        CheckConstraint("views >= 0", name="check_views"),
        CheckConstraint("likes >= 0", name="check_likes"),
        CheckConstraint("comments >= 0", name="check_comments"),
        CheckConstraint("saves >= 0", name="check_saves"),
        CheckConstraint("shares >= 0", name="check_shares"),
        CheckConstraint("mileage >= 0", name="check_mileage"),
        CheckConstraint("condition IN ('new', 'used', 'certified', 'salvage', 'other')", name="check_condition"),
        {"extend_existing": True}
    )
    
    def __repr__(self):
        return f"<Listing(id={self.id}, platform={self.platform}, make={self.make}, model={self.model}, price={self.price})>"
    
    @property
    def engagement_score(self) -> float:
        """Calculate engagement score"""
        return (
            (self.views or 0) * 1.0 +
            (self.likes or 0) * 3.0 +
            (self.comments or 0) * 5.0 +
            (self.saves or 0) * 2.0 +
            (self.shares or 0) * 4.0
        )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "platform": self.platform,
            "external_id": self.external_id,
            "title": self.title,
            "description": self.description,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "price": float(self.price) if self.price else None,
            "currency": self.currency,
            "condition": self.condition,
            "mileage": self.mileage,
            "location": self.location,
            "url": self.url,
            "images": self.images or [],
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "saves": self.saves,
            "shares": self.shares,
            "engagement_score": self.engagement_score,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "is_active": self.is_active,
            "is_duplicate": self.is_duplicate
        }
