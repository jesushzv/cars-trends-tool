"""
Trend schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal


class TrendBase(BaseModel):
    """Base trend schema"""
    make: str
    model: str
    date: date
    
    # Aggregated metrics
    total_listings: int = 0
    avg_price: Optional[Decimal] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    total_views: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_saves: int = 0
    total_shares: int = 0
    engagement_score: Decimal = 0
    
    # Calculated metrics
    price_change_pct: Optional[Decimal] = None
    listing_change_pct: Optional[Decimal] = None
    engagement_change_pct: Optional[Decimal] = None


class TrendCreate(TrendBase):
    """Trend creation schema"""
    pass


class TrendUpdate(BaseModel):
    """Trend update schema"""
    total_listings: Optional[int] = None
    avg_price: Optional[Decimal] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    total_views: Optional[int] = None
    total_likes: Optional[int] = None
    total_comments: Optional[int] = None
    total_saves: Optional[int] = None
    total_shares: Optional[int] = None
    engagement_score: Optional[Decimal] = None
    price_change_pct: Optional[Decimal] = None
    listing_change_pct: Optional[Decimal] = None
    engagement_change_pct: Optional[Decimal] = None


class TrendResponse(TrendBase):
    """Trend response schema"""
    id: str
    
    class Config:
        from_attributes = True


class TrendFilters(BaseModel):
    """Trend filters schema"""
    make: Optional[str] = None
    model: Optional[str] = None
    days_back: int = 30


class TrendSummary(BaseModel):
    """Trend summary schema"""
    total_trends: int
    unique_makes: int
    unique_models: int
    avg_engagement_score: float
    top_makes: list
    top_models: list
