"""
Trend model for aggregated daily trends by make/model
"""

from sqlalchemy import Column, String, Integer, DECIMAL, Date, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid


class Trend(Base):
    """Daily trend model for car makes/models"""
    
    __tablename__ = "trends"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    make = Column(String(50), nullable=False, index=True)
    model = Column(String(50), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # Aggregated metrics
    total_listings = Column(Integer, default=0)
    avg_price = Column(DECIMAL(12, 2))
    min_price = Column(DECIMAL(12, 2))
    max_price = Column(DECIMAL(12, 2))
    total_views = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_saves = Column(Integer, default=0)
    total_shares = Column(Integer, default=0)
    engagement_score = Column(DECIMAL(10, 2), default=0)
    
    # Calculated metrics
    price_change_pct = Column(DECIMAL(5, 2))
    listing_change_pct = Column(DECIMAL(5, 2))
    engagement_change_pct = Column(DECIMAL(5, 2))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("total_listings >= 0", name="check_total_listings"),
        CheckConstraint("avg_price >= 0", name="check_avg_price"),
        CheckConstraint("min_price >= 0", name="check_min_price"),
        CheckConstraint("max_price >= 0", name="check_max_price"),
        CheckConstraint("total_views >= 0", name="check_total_views"),
        CheckConstraint("total_likes >= 0", name="check_total_likes"),
        CheckConstraint("total_comments >= 0", name="check_total_comments"),
        CheckConstraint("total_saves >= 0", name="check_total_saves"),
        CheckConstraint("total_shares >= 0", name="check_total_shares"),
        CheckConstraint("engagement_score >= 0", name="check_engagement_score"),
        CheckConstraint("min_price <= max_price", name="check_price_range"),
        {"extend_existing": True}
    )
    
    def __repr__(self):
        return f"<Trend(make={self.make}, model={self.model}, date={self.date}, listings={self.total_listings})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "make": self.make,
            "model": self.model,
            "date": self.date.isoformat() if self.date else None,
            "total_listings": self.total_listings,
            "avg_price": float(self.avg_price) if self.avg_price else None,
            "min_price": float(self.min_price) if self.min_price else None,
            "max_price": float(self.max_price) if self.max_price else None,
            "total_views": self.total_views,
            "total_likes": self.total_likes,
            "total_comments": self.total_comments,
            "total_saves": self.total_saves,
            "total_shares": self.total_shares,
            "engagement_score": float(self.engagement_score) if self.engagement_score else 0,
            "price_change_pct": float(self.price_change_pct) if self.price_change_pct else None,
            "listing_change_pct": float(self.listing_change_pct) if self.listing_change_pct else None,
            "engagement_change_pct": float(self.engagement_change_pct) if self.engagement_change_pct else None
        }
