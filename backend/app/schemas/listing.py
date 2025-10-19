"""
Listing schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ListingBase(BaseModel):
    """Base listing schema"""
    platform: str
    external_id: str
    title: str
    description: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[Decimal] = None
    currency: str = "MXN"
    condition: Optional[str] = None
    mileage: Optional[int] = None
    location: Optional[str] = None
    url: str
    images: Optional[List[str]] = None
    
    # Engagement metrics
    views: int = 0
    likes: int = 0
    comments: int = 0
    saves: int = 0
    shares: int = 0
    
    # Metadata
    posted_date: Optional[datetime] = None
    is_active: bool = True
    is_duplicate: bool = False


class ListingCreate(ListingBase):
    """Listing creation schema"""
    pass


class ListingUpdate(BaseModel):
    """Listing update schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[Decimal] = None
    condition: Optional[str] = None
    mileage: Optional[int] = None
    location: Optional[str] = None
    images: Optional[List[str]] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    saves: Optional[int] = None
    shares: Optional[int] = None
    is_active: Optional[bool] = None
    is_duplicate: Optional[bool] = None


class ListingResponse(ListingBase):
    """Listing response schema"""
    id: str
    engagement_score: float
    scraped_at: datetime
    
    class Config:
        from_attributes = True


class ListingFilters(BaseModel):
    """Listing filters schema"""
    platform: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    condition: Optional[str] = None
    days_back: int = 30
    
    @validator('platform')
    def validate_platform(cls, v):
        if v and v not in ['facebook', 'craigslist', 'mercadolibre']:
            raise ValueError('Invalid platform')
        return v
    
    @validator('condition')
    def validate_condition(cls, v):
        if v and v not in ['new', 'used', 'certified', 'salvage', 'other']:
            raise ValueError('Invalid condition')
        return v


class ListingSummary(BaseModel):
    """Listing summary schema"""
    total_listings: int
    total_views: int
    total_likes: int
    total_comments: int
    avg_price: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    platforms: dict
    makes: dict
    conditions: dict
