"""
Listings endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.listing import Listing
from app.schemas.listing import ListingResponse, ListingFilters
from app.services.listing_service import ListingService
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[ListingResponse])
async def get_listings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    make: Optional[str] = Query(None, description="Filter by car make"),
    model: Optional[str] = Query(None, description="Filter by car model"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    min_year: Optional[int] = Query(None, ge=1900, description="Minimum year"),
    max_year: Optional[int] = Query(None, ge=1900, description="Maximum year"),
    condition: Optional[str] = Query(None, description="Filter by condition"),
    days_back: int = Query(30, ge=1, le=365, description="Number of days back to search"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get listings with optional filters"""
    listing_service = ListingService(db)
    
    filters = ListingFilters(
        platform=platform,
        make=make,
        model=model,
        min_price=min_price,
        max_price=max_price,
        min_year=min_year,
        max_year=max_year,
        condition=condition,
        days_back=days_back
    )
    
    listings = await listing_service.get_listings(
        skip=skip,
        limit=limit,
        filters=filters
    )
    
    return listings


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific listing by ID"""
    listing_service = ListingService(db)
    
    listing = await listing_service.get_listing_by_id(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return listing


@router.get("/platform/{platform}", response_model=List[ListingResponse])
async def get_listings_by_platform(
    platform: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get listings from a specific platform"""
    if platform not in ['facebook', 'craigslist', 'mercadolibre']:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    listing_service = ListingService(db)
    
    filters = ListingFilters(platform=platform, days_back=days_back)
    listings = await listing_service.get_listings(
        skip=skip,
        limit=limit,
        filters=filters
    )
    
    return listings


@router.get("/top/engagement", response_model=List[ListingResponse])
async def get_top_listings_by_engagement(
    limit: int = Query(20, ge=1, le=100),
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top listings by engagement score"""
    listing_service = ListingService(db)
    
    filters = ListingFilters(days_back=days_back)
    listings = await listing_service.get_top_listings_by_engagement(
        limit=limit,
        filters=filters
    )
    
    return listings


@router.get("/stats/summary")
async def get_listings_summary(
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get listings summary statistics"""
    listing_service = ListingService(db)
    
    filters = ListingFilters(days_back=days_back)
    summary = await listing_service.get_listings_summary(filters)
    
    return summary
