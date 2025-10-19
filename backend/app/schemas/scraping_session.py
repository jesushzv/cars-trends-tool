"""
Scraping session schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class ScrapingSessionBase(BaseModel):
    """Base scraping session schema"""
    platform: str
    status: str = "running"
    listings_found: int = 0
    listings_processed: int = 0
    listings_new: int = 0
    listings_updated: int = 0
    errors: Optional[List[str]] = None
    execution_time_seconds: Optional[int] = None


class ScrapingSessionCreate(ScrapingSessionBase):
    """Scraping session creation schema"""
    pass


class ScrapingSessionUpdate(BaseModel):
    """Scraping session update schema"""
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    listings_found: Optional[int] = None
    listings_processed: Optional[int] = None
    listings_new: Optional[int] = None
    listings_updated: Optional[int] = None
    errors: Optional[List[str]] = None
    execution_time_seconds: Optional[int] = None


class ScrapingSessionResponse(ScrapingSessionBase):
    """Scraping session response schema"""
    id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ScrapingStats(BaseModel):
    """Scraping statistics schema"""
    total_sessions: int
    successful_sessions: int
    failed_sessions: int
    total_listings_found: int
    total_listings_processed: int
    avg_execution_time: Optional[float] = None
    platform_stats: dict
