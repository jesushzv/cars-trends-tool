"""
Trend service for managing car trends
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, asc
from typing import List, Optional
from datetime import datetime, timedelta, date
import logging

from app.models.trend import Trend
from app.schemas.trend import TrendFilters, TrendSummary

logger = logging.getLogger(__name__)


class TrendService:
    """Trend service for managing car trends"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_trends(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[TrendFilters] = None
    ) -> List[Trend]:
        """Get trends with filters"""
        query = select(Trend)
        
        if filters:
            # Date filter
            if filters.days_back:
                cutoff_date = date.today() - timedelta(days=filters.days_back)
                query = query.where(Trend.date >= cutoff_date)
            
            # Make filter
            if filters.make:
                query = query.where(Trend.make.ilike(f"%{filters.make}%"))
            
            # Model filter
            if filters.model:
                query = query.where(Trend.model.ilike(f"%{filters.model}%"))
        
        # Order by date and engagement score
        query = query.order_by(desc(Trend.date), desc(Trend.engagement_score))
        
        # Pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_trends_by_make_model(self, filters: TrendFilters) -> List[Trend]:
        """Get trends for a specific make and model"""
        if not filters.make or not filters.model:
            return []
        
        query = select(Trend).where(
            and_(
                Trend.make.ilike(f"%{filters.make}%"),
                Trend.model.ilike(f"%{filters.model}%")
            )
        )
        
        if filters.days_back:
            cutoff_date = date.today() - timedelta(days=filters.days_back)
            query = query.where(Trend.date >= cutoff_date)
        
        query = query.order_by(asc(Trend.date))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_top_trends_by_engagement(
        self,
        limit: int = 20,
        filters: Optional[TrendFilters] = None
    ) -> List[Trend]:
        """Get top trends by engagement score"""
        query = select(Trend)
        
        if filters:
            # Date filter
            if filters.days_back:
                cutoff_date = date.today() - timedelta(days=filters.days_back)
                query = query.where(Trend.date >= cutoff_date)
            
            # Make filter
            if filters.make:
                query = query.where(Trend.make.ilike(f"%{filters.make}%"))
            
            # Model filter
            if filters.model:
                query = query.where(Trend.model.ilike(f"%{filters.model}%"))
        
        # Order by engagement score
        query = query.order_by(desc(Trend.engagement_score))
        
        # Limit results
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_trends_summary(self, filters: Optional[TrendFilters] = None) -> TrendSummary:
        """Get trends summary statistics"""
        query = select(Trend)
        
        if filters:
            # Date filter
            if filters.days_back:
                cutoff_date = date.today() - timedelta(days=filters.days_back)
                query = query.where(Trend.date >= cutoff_date)
            
            # Make filter
            if filters.make:
                query = query.where(Trend.make.ilike(f"%{filters.make}%"))
            
            # Model filter
            if filters.model:
                query = query.where(Trend.model.ilike(f"%{filters.model}%"))
        
        # Get basic counts
        total_result = await self.db.execute(
            select(func.count(Trend.id)).select_from(query.subquery())
        )
        total_trends = total_result.scalar()
        
        # Get unique makes and models
        unique_result = await self.db.execute(
            select(
                func.count(func.distinct(Trend.make)).label('unique_makes'),
                func.count(func.distinct(Trend.model)).label('unique_models')
            ).select_from(query.subquery())
        )
        unique_data = unique_result.first()
        
        # Get average engagement score
        engagement_result = await self.db.execute(
            select(func.avg(Trend.engagement_score)).select_from(query.subquery())
        )
        avg_engagement = engagement_result.scalar()
        
        # Get top makes
        top_makes_result = await self.db.execute(
            select(
                Trend.make,
                func.sum(Trend.engagement_score).label('total_engagement')
            ).select_from(query.subquery())
            .group_by(Trend.make)
            .order_by(desc('total_engagement'))
            .limit(10)
        )
        top_makes = [{"make": row.make, "engagement": float(row.total_engagement)} for row in top_makes_result]
        
        # Get top models
        top_models_result = await self.db.execute(
            select(
                Trend.make,
                Trend.model,
                func.sum(Trend.engagement_score).label('total_engagement')
            ).select_from(query.subquery())
            .group_by(Trend.make, Trend.model)
            .order_by(desc('total_engagement'))
            .limit(10)
        )
        top_models = [{"make": row.make, "model": row.model, "engagement": float(row.total_engagement)} for row in top_models_result]
        
        return TrendSummary(
            total_trends=total_trends or 0,
            unique_makes=unique_data.unique_makes or 0,
            unique_models=unique_data.unique_models or 0,
            avg_engagement_score=float(avg_engagement) if avg_engagement else 0,
            top_makes=top_makes,
            top_models=top_models
        )
    
    async def create_trend(self, trend_data: dict) -> Trend:
        """Create a new trend"""
        trend = Trend(**trend_data)
        self.db.add(trend)
        await self.db.commit()
        await self.db.refresh(trend)
        return trend
    
    async def update_trend(self, trend_id: str, update_data: dict) -> Optional[Trend]:
        """Update a trend"""
        result = await self.db.execute(
            select(Trend).where(Trend.id == trend_id)
        )
        trend = result.scalar_one_or_none()
        if not trend:
            return None
        
        for key, value in update_data.items():
            if hasattr(trend, key):
                setattr(trend, key, value)
        
        await self.db.commit()
        await self.db.refresh(trend)
        return trend
