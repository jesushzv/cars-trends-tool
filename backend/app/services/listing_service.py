"""
Listing service for managing car listings
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.models.listing import Listing
from app.schemas.listing import ListingFilters, ListingSummary

logger = logging.getLogger(__name__)


class ListingService:
    """Listing service for managing car listings"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_listing_by_id(self, listing_id: str) -> Optional[Listing]:
        """Get listing by ID"""
        result = await self.db.execute(
            select(Listing).where(Listing.id == listing_id)
        )
        return result.scalar_one_or_none()
    
    async def get_listings(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[ListingFilters] = None
    ) -> List[Listing]:
        """Get listings with filters"""
        query = select(Listing)
        
        if filters:
            # Date filter
            if filters.days_back:
                cutoff_date = datetime.utcnow() - timedelta(days=filters.days_back)
                query = query.where(Listing.scraped_at >= cutoff_date)
            
            # Platform filter
            if filters.platform:
                query = query.where(Listing.platform == filters.platform)
            
            # Make filter
            if filters.make:
                query = query.where(Listing.make.ilike(f"%{filters.make}%"))
            
            # Model filter
            if filters.model:
                query = query.where(Listing.model.ilike(f"%{filters.model}%"))
            
            # Price filters
            if filters.min_price is not None:
                query = query.where(Listing.price >= filters.min_price)
            if filters.max_price is not None:
                query = query.where(Listing.price <= filters.max_price)
            
            # Year filters
            if filters.min_year is not None:
                query = query.where(Listing.year >= filters.min_year)
            if filters.max_year is not None:
                query = query.where(Listing.year <= filters.max_year)
            
            # Condition filter
            if filters.condition:
                query = query.where(Listing.condition == filters.condition)
        
        # Only active listings
        query = query.where(Listing.is_active == True)
        
        # Order by engagement score and scraped date
        query = query.order_by(desc(Listing.scraped_at))
        
        # Pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_top_listings_by_engagement(
        self,
        limit: int = 20,
        filters: Optional[ListingFilters] = None
    ) -> List[Listing]:
        """Get top listings by engagement score"""
        query = select(Listing)
        
        if filters:
            # Date filter
            if filters.days_back:
                cutoff_date = datetime.utcnow() - timedelta(days=filters.days_back)
                query = query.where(Listing.scraped_at >= cutoff_date)
            
            # Platform filter
            if filters.platform:
                query = query.where(Listing.platform == filters.platform)
            
            # Make filter
            if filters.make:
                query = query.where(Listing.make.ilike(f"%{filters.make}%"))
            
            # Model filter
            if filters.model:
                query = query.where(Listing.model.ilike(f"%{filters.model}%"))
        
        # Only active listings with engagement data
        query = query.where(
            and_(
                Listing.is_active == True,
                or_(
                    Listing.views > 0,
                    Listing.likes > 0,
                    Listing.comments > 0
                )
            )
        )
        
        # Order by engagement score (calculated)
        query = query.order_by(
            desc(
                (Listing.views * 1.0) +
                (Listing.likes * 3.0) +
                (Listing.comments * 5.0) +
                (Listing.saves * 2.0) +
                (Listing.shares * 4.0)
            )
        )
        
        # Limit results
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_listings_summary(self, filters: Optional[ListingFilters] = None) -> ListingSummary:
        """Get listings summary statistics"""
        query = select(Listing)
        
        if filters:
            # Date filter
            if filters.days_back:
                cutoff_date = datetime.utcnow() - timedelta(days=filters.days_back)
                query = query.where(Listing.scraped_at >= cutoff_date)
            
            # Platform filter
            if filters.platform:
                query = query.where(Listing.platform == filters.platform)
            
            # Make filter
            if filters.make:
                query = query.where(Listing.make.ilike(f"%{filters.make}%"))
            
            # Model filter
            if filters.model:
                query = query.where(Listing.model.ilike(f"%{filters.model}%"))
        
        # Only active listings
        query = query.where(Listing.is_active == True)
        
        # Get basic counts
        total_result = await self.db.execute(
            select(func.count(Listing.id)).select_from(query.subquery())
        )
        total_listings = total_result.scalar()
        
        # Get engagement totals
        engagement_result = await self.db.execute(
            select(
                func.sum(Listing.views).label('total_views'),
                func.sum(Listing.likes).label('total_likes'),
                func.sum(Listing.comments).label('total_comments')
            ).select_from(query.subquery())
        )
        engagement_data = engagement_result.first()
        
        # Get price statistics
        price_result = await self.db.execute(
            select(
                func.avg(Listing.price).label('avg_price'),
                func.min(Listing.price).label('min_price'),
                func.max(Listing.price).label('max_price')
            ).select_from(query.subquery())
        )
        price_data = price_result.first()
        
        # Get platform distribution
        platform_result = await self.db.execute(
            select(
                Listing.platform,
                func.count(Listing.id).label('count')
            ).select_from(query.subquery())
            .group_by(Listing.platform)
        )
        platforms = {row.platform: row.count for row in platform_result}
        
        # Get make distribution
        make_result = await self.db.execute(
            select(
                Listing.make,
                func.count(Listing.id).label('count')
            ).select_from(query.subquery())
            .where(Listing.make.isnot(None))
            .group_by(Listing.make)
            .order_by(desc('count'))
            .limit(10)
        )
        makes = {row.make: row.count for row in make_result}
        
        # Get condition distribution
        condition_result = await self.db.execute(
            select(
                Listing.condition,
                func.count(Listing.id).label('count')
            ).select_from(query.subquery())
            .where(Listing.condition.isnot(None))
            .group_by(Listing.condition)
        )
        conditions = {row.condition: row.count for row in condition_result}
        
        return ListingSummary(
            total_listings=total_listings or 0,
            total_views=engagement_data.total_views or 0,
            total_likes=engagement_data.total_likes or 0,
            total_comments=engagement_data.total_comments or 0,
            avg_price=float(price_data.avg_price) if price_data.avg_price else None,
            min_price=float(price_data.min_price) if price_data.min_price else None,
            max_price=float(price_data.max_price) if price_data.max_price else None,
            platforms=platforms,
            makes=makes,
            conditions=conditions
        )
    
    async def create_listing(self, listing_data: dict) -> Listing:
        """Create a new listing"""
        listing = Listing(**listing_data)
        self.db.add(listing)
        await self.db.commit()
        await self.db.refresh(listing)
        return listing
    
    async def update_listing(self, listing_id: str, update_data: dict) -> Optional[Listing]:
        """Update a listing"""
        listing = await self.get_listing_by_id(listing_id)
        if not listing:
            return None
        
        for key, value in update_data.items():
            if hasattr(listing, key):
                setattr(listing, key, value)
        
        await self.db.commit()
        await self.db.refresh(listing)
        return listing
