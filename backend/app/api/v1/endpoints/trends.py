"""
Trends endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.trend import Trend
from app.schemas.trend import TrendResponse, TrendFilters
from app.services.trend_service import TrendService
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[TrendResponse])
async def get_trends(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    make: Optional[str] = Query(None, description="Filter by car make"),
    model: Optional[str] = Query(None, description="Filter by car model"),
    days_back: int = Query(30, ge=1, le=365, description="Number of days back to search"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trends with optional filters"""
    trend_service = TrendService(db)
    
    filters = TrendFilters(
        make=make,
        model=model,
        days_back=days_back
    )
    
    trends = await trend_service.get_trends(
        skip=skip,
        limit=limit,
        filters=filters
    )
    
    return trends


@router.get("/{make}/{model}", response_model=List[TrendResponse])
async def get_trends_by_make_model(
    make: str,
    model: str,
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trends for a specific make and model"""
    trend_service = TrendService(db)
    
    filters = TrendFilters(make=make, model=model, days_back=days_back)
    trends = await trend_service.get_trends_by_make_model(filters)
    
    return trends


@router.get("/top/engagement", response_model=List[TrendResponse])
async def get_top_trends_by_engagement(
    limit: int = Query(20, ge=1, le=100),
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top trends by engagement score"""
    trend_service = TrendService(db)
    
    filters = TrendFilters(days_back=days_back)
    trends = await trend_service.get_top_trends_by_engagement(
        limit=limit,
        filters=filters
    )
    
    return trends


@router.get("/stats/summary")
async def get_trends_summary(
    days_back: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trends summary statistics"""
    trend_service = TrendService(db)
    
    filters = TrendFilters(days_back=days_back)
    summary = await trend_service.get_trends_summary(filters)
    
    return summary
