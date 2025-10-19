"""
Analytics service for generating insights and reports
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, asc, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import logging

from app.models.listing import Listing
from app.models.trend import Trend

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Analytics service for generating insights"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_top_cars_by_engagement(
        self,
        limit: int = 20,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Get top cars by engagement metrics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = select(
            Listing.make,
            Listing.model,
            func.count(Listing.id).label('total_listings'),
            func.avg(Listing.price).label('avg_price'),
            func.sum(Listing.views).label('total_views'),
            func.sum(Listing.likes).label('total_likes'),
            func.sum(Listing.comments).label('total_comments'),
            func.sum(Listing.saves).label('total_saves'),
            func.sum(Listing.shares).label('total_shares'),
            func.sum(
                (Listing.views * 1.0) +
                (Listing.likes * 3.0) +
                (Listing.comments * 5.0) +
                (Listing.saves * 2.0) +
                (Listing.shares * 4.0)
            ).label('engagement_score')
        ).where(
            and_(
                Listing.is_active == True,
                Listing.scraped_at >= cutoff_date,
                Listing.make.isnot(None),
                Listing.model.isnot(None)
            )
        ).group_by(
            Listing.make, Listing.model
        ).having(
            func.count(Listing.id) >= 3  # Minimum 3 listings
        ).order_by(
            desc('engagement_score')
        ).limit(limit)
        
        result = await self.db.execute(query)
        return [
            {
                "make": row.make,
                "model": row.model,
                "total_listings": row.total_listings,
                "avg_price": float(row.avg_price) if row.avg_price else None,
                "total_views": row.total_views,
                "total_likes": row.total_likes,
                "total_comments": row.total_comments,
                "total_saves": row.total_saves,
                "total_shares": row.total_shares,
                "engagement_score": float(row.engagement_score)
            }
            for row in result
        ]
    
    async def get_price_trends(
        self,
        make: Optional[str] = None,
        model: Optional[str] = None,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Get price trends over time"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = select(
            func.date(Listing.scraped_at).label('date'),
            func.avg(Listing.price).label('avg_price'),
            func.min(Listing.price).label('min_price'),
            func.max(Listing.price).label('max_price'),
            func.count(Listing.id).label('total_listings')
        ).where(
            and_(
                Listing.is_active == True,
                Listing.scraped_at >= cutoff_date,
                Listing.price.isnot(None)
            )
        )
        
        if make:
            query = query.where(Listing.make.ilike(f"%{make}%"))
        if model:
            query = query.where(Listing.model.ilike(f"%{model}%"))
        
        query = query.group_by(
            func.date(Listing.scraped_at)
        ).order_by(
            asc('date')
        )
        
        result = await self.db.execute(query)
        return [
            {
                "date": row.date.isoformat(),
                "avg_price": float(row.avg_price) if row.avg_price else None,
                "min_price": float(row.min_price) if row.min_price else None,
                "max_price": float(row.max_price) if row.max_price else None,
                "total_listings": row.total_listings
            }
            for row in result
        ]
    
    async def get_market_share(
        self,
        days_back: int = 30,
        group_by: str = "make"
    ) -> List[Dict[str, Any]]:
        """Get market share analysis"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        if group_by == "make":
            group_field = Listing.make
        elif group_by == "model":
            group_field = Listing.model
        else:
            raise ValueError("group_by must be 'make' or 'model'")
        
        # Get total listings for percentage calculation
        total_result = await self.db.execute(
            select(func.count(Listing.id)).where(
                and_(
                    Listing.is_active == True,
                    Listing.scraped_at >= cutoff_date,
                    group_field.isnot(None)
                )
            )
        )
        total_listings = total_result.scalar()
        
        if total_listings == 0:
            return []
        
        query = select(
            group_field.label('name'),
            func.count(Listing.id).label('count'),
            func.avg(Listing.price).label('avg_price'),
            func.sum(
                (Listing.views * 1.0) +
                (Listing.likes * 3.0) +
                (Listing.comments * 5.0) +
                (Listing.saves * 2.0) +
                (Listing.shares * 4.0)
            ).label('total_engagement')
        ).where(
            and_(
                Listing.is_active == True,
                Listing.scraped_at >= cutoff_date,
                group_field.isnot(None)
            )
        ).group_by(
            group_field
        ).order_by(
            desc('count')
        ).limit(20)
        
        result = await self.db.execute(query)
        return [
            {
                "name": row.name,
                "count": row.count,
                "percentage": round((row.count / total_listings) * 100, 2),
                "avg_price": float(row.avg_price) if row.avg_price else None,
                "total_engagement": float(row.total_engagement) if row.total_engagement else 0
            }
            for row in result
        ]
    
    async def get_engagement_analysis(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get engagement analysis across platforms"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Platform engagement analysis
        platform_query = select(
            Listing.platform,
            func.count(Listing.id).label('total_listings'),
            func.avg(Listing.views).label('avg_views'),
            func.avg(Listing.likes).label('avg_likes'),
            func.avg(Listing.comments).label('avg_comments'),
            func.avg(
                (Listing.views * 1.0) +
                (Listing.likes * 3.0) +
                (Listing.comments * 5.0) +
                (Listing.saves * 2.0) +
                (Listing.shares * 4.0)
            ).label('avg_engagement_score')
        ).where(
            and_(
                Listing.is_active == True,
                Listing.scraped_at >= cutoff_date
            )
        ).group_by(
            Listing.platform
        )
        
        platform_result = await self.db.execute(platform_query)
        platform_analysis = [
            {
                "platform": row.platform,
                "total_listings": row.total_listings,
                "avg_views": float(row.avg_views) if row.avg_views else 0,
                "avg_likes": float(row.avg_likes) if row.avg_likes else 0,
                "avg_comments": float(row.avg_comments) if row.avg_comments else 0,
                "avg_engagement_score": float(row.avg_engagement_score) if row.avg_engagement_score else 0
            }
            for row in platform_result
        ]
        
        # Overall engagement metrics
        overall_query = select(
            func.count(Listing.id).label('total_listings'),
            func.sum(Listing.views).label('total_views'),
            func.sum(Listing.likes).label('total_likes'),
            func.sum(Listing.comments).label('total_comments'),
            func.sum(Listing.saves).label('total_saves'),
            func.sum(Listing.shares).label('total_shares')
        ).where(
            and_(
                Listing.is_active == True,
                Listing.scraped_at >= cutoff_date
            )
        )
        
        overall_result = await self.db.execute(overall_query)
        overall_data = overall_result.first()
        
        return {
            "platform_analysis": platform_analysis,
            "overall_metrics": {
                "total_listings": overall_data.total_listings or 0,
                "total_views": overall_data.total_views or 0,
                "total_likes": overall_data.total_likes or 0,
                "total_comments": overall_data.total_comments or 0,
                "total_saves": overall_data.total_saves or 0,
                "total_shares": overall_data.total_shares or 0
            }
        }
    
    async def get_listing_frequency(
        self,
        make: Optional[str] = None,
        model: Optional[str] = None,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Get listing frequency analysis"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = select(
            func.date(Listing.scraped_at).label('date'),
            func.count(Listing.id).label('new_listings'),
            func.avg(Listing.price).label('avg_price')
        ).where(
            and_(
                Listing.is_active == True,
                Listing.scraped_at >= cutoff_date
            )
        )
        
        if make:
            query = query.where(Listing.make.ilike(f"%{make}%"))
        if model:
            query = query.where(Listing.model.ilike(f"%{model}%"))
        
        query = query.group_by(
            func.date(Listing.scraped_at)
        ).order_by(
            asc('date')
        )
        
        result = await self.db.execute(query)
        return [
            {
                "date": row.date.isoformat(),
                "new_listings": row.new_listings,
                "avg_price": float(row.avg_price) if row.avg_price else None
            }
            for row in result
        ]
    
    async def get_dashboard_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get top cars by engagement
        top_cars = await self.get_top_cars_by_engagement(limit=10, days_back=days_back)
        
        # Get market share
        market_share = await self.get_market_share(days_back=days_back, group_by="make")
        
        # Get price trends
        price_trends = await self.get_price_trends(days_back=days_back)
        
        # Get engagement analysis
        engagement_analysis = await self.get_engagement_analysis(days_back=days_back)
        
        # Get listing frequency
        listing_frequency = await self.get_listing_frequency(days_back=days_back)
        
        return {
            "top_cars": top_cars,
            "market_share": market_share,
            "price_trends": price_trends,
            "engagement_analysis": engagement_analysis,
            "listing_frequency": listing_frequency,
            "summary_period": f"Last {days_back} days"
        }
