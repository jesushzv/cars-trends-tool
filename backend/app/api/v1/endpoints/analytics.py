"""
Analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/top-cars")
async def get_top_cars_by_engagement(
    limit: int = Query(20, ge=1, le=100),
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top cars by engagement metrics"""
    analytics_service = AnalyticsService(db)
    
    top_cars = await analytics_service.get_top_cars_by_engagement(
        limit=limit,
        days_back=days_back
    )
    
    return top_cars


@router.get("/price-trends")
async def get_price_trends(
    make: Optional[str] = Query(None, description="Filter by car make"),
    model: Optional[str] = Query(None, description="Filter by car model"),
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price trends over time"""
    analytics_service = AnalyticsService(db)
    
    price_trends = await analytics_service.get_price_trends(
        make=make,
        model=model,
        days_back=days_back
    )
    
    return price_trends


@router.get("/market-share")
async def get_market_share(
    days_back: int = Query(30, ge=1, le=365),
    by: str = Query("make", description="Group by 'make' or 'model'"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get market share analysis"""
    if by not in ['make', 'model']:
        raise HTTPException(status_code=400, detail="Invalid 'by' parameter. Must be 'make' or 'model'")
    
    analytics_service = AnalyticsService(db)
    
    market_share = await analytics_service.get_market_share(
        days_back=days_back,
        group_by=by
    )
    
    return market_share


@router.get("/engagement-analysis")
async def get_engagement_analysis(
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get engagement analysis across platforms"""
    analytics_service = AnalyticsService(db)
    
    engagement_analysis = await analytics_service.get_engagement_analysis(
        days_back=days_back
    )
    
    return engagement_analysis


@router.get("/listing-frequency")
async def get_listing_frequency(
    make: Optional[str] = Query(None, description="Filter by car make"),
    model: Optional[str] = Query(None, description="Filter by car model"),
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get listing frequency analysis"""
    analytics_service = AnalyticsService(db)
    
    listing_frequency = await analytics_service.get_listing_frequency(
        make=make,
        model=model,
        days_back=days_back
    )
    
    return listing_frequency


@router.get("/dashboard-summary")
async def get_dashboard_summary(
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard summary"""
    analytics_service = AnalyticsService(db)
    
    summary = await analytics_service.get_dashboard_summary(
        days_back=days_back
    )
    
    return summary
