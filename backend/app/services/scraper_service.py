"""
Scraper service for managing scraping operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import asyncio

from app.models.scraping_session import ScrapingSession
from app.schemas.scraping_session import ScrapingStats
from app.scrapers.facebook_marketplace import FacebookMarketplaceScraper
from app.scrapers.craigslist import CraigslistScraper
from app.scrapers.mercadolibre import MercadoLibreScraper

logger = logging.getLogger(__name__)


class ScraperService:
    """Scraper service for managing scraping operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.scrapers = {
            'facebook': FacebookMarketplaceScraper(db),
            'craigslist': CraigslistScraper(db),
            'mercadolibre': MercadoLibreScraper(db)
        }
    
    async def scrape_platform(self, platform: str) -> ScrapingSession:
        """Scrape a specific platform"""
        if platform not in self.scrapers:
            raise ValueError(f"Unknown platform: {platform}")
        
        # Create scraping session
        session = ScrapingSession(platform=platform, status="running")
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting scraping for {platform}")
            
            # Run the scraper
            scraper = self.scrapers[platform]
            result = await scraper.scrape()
            
            # Update session with results
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            session.listings_found = result.get('listings_found', 0)
            session.listings_processed = result.get('listings_processed', 0)
            session.listings_new = result.get('listings_new', 0)
            session.listings_updated = result.get('listings_updated', 0)
            session.errors = result.get('errors', [])
            session.execution_time_seconds = int((datetime.utcnow() - start_time).total_seconds())
            
            await self.db.commit()
            
            logger.info(f"Completed scraping for {platform}: {session.listings_processed} listings processed")
            
        except Exception as e:
            logger.error(f"Scraping failed for {platform}: {e}")
            
            # Update session with error
            session.status = "failed"
            session.completed_at = datetime.utcnow()
            session.errors = [str(e)]
            session.execution_time_seconds = int((datetime.utcnow() - start_time).total_seconds())
            
            await self.db.commit()
        
        return session
    
    async def scrape_all_platforms(self) -> List[ScrapingSession]:
        """Scrape all platforms concurrently"""
        logger.info("Starting scraping for all platforms")
        
        # Run all scrapers concurrently
        tasks = []
        for platform in self.scrapers.keys():
            task = asyncio.create_task(self.scrape_platform(platform))
            tasks.append(task)
        
        # Wait for all tasks to complete
        sessions = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return only successful sessions
        successful_sessions = []
        for session in sessions:
            if isinstance(session, ScrapingSession):
                successful_sessions.append(session)
            else:
                logger.error(f"Scraping task failed: {session}")
        
        logger.info(f"Completed scraping for all platforms: {len(successful_sessions)} successful")
        return successful_sessions
    
    async def get_recent_sessions(self, limit: int = 10) -> List[ScrapingSession]:
        """Get recent scraping sessions"""
        result = await self.db.execute(
            select(ScrapingSession)
            .order_by(desc(ScrapingSession.started_at))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_scraping_history(
        self,
        platform: Optional[str] = None,
        limit: int = 50
    ) -> List[ScrapingSession]:
        """Get scraping history"""
        query = select(ScrapingSession)
        
        if platform:
            query = query.where(ScrapingSession.platform == platform)
        
        query = query.order_by(desc(ScrapingSession.started_at)).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_scraping_stats(self, days_back: int = 30) -> ScrapingStats:
        """Get scraping statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get total sessions
        total_result = await self.db.execute(
            select(func.count(ScrapingSession.id))
            .where(ScrapingSession.started_at >= cutoff_date)
        )
        total_sessions = total_result.scalar()
        
        # Get successful sessions
        successful_result = await self.db.execute(
            select(func.count(ScrapingSession.id))
            .where(
                ScrapingSession.started_at >= cutoff_date,
                ScrapingSession.status == "completed"
            )
        )
        successful_sessions = successful_result.scalar()
        
        # Get failed sessions
        failed_result = await self.db.execute(
            select(func.count(ScrapingSession.id))
            .where(
                ScrapingSession.started_at >= cutoff_date,
                ScrapingSession.status == "failed"
            )
        )
        failed_sessions = failed_result.scalar()
        
        # Get total listings found and processed
        listings_result = await self.db.execute(
            select(
                func.sum(ScrapingSession.listings_found).label('total_found'),
                func.sum(ScrapingSession.listings_processed).label('total_processed')
            )
            .where(ScrapingSession.started_at >= cutoff_date)
        )
        listings_data = listings_result.first()
        
        # Get average execution time
        time_result = await self.db.execute(
            select(func.avg(ScrapingSession.execution_time_seconds))
            .where(
                ScrapingSession.started_at >= cutoff_date,
                ScrapingSession.execution_time_seconds.isnot(None)
            )
        )
        avg_execution_time = time_result.scalar()
        
        # Get platform stats
        platform_result = await self.db.execute(
            select(
                ScrapingSession.platform,
                func.count(ScrapingSession.id).label('sessions'),
                func.sum(ScrapingSession.listings_processed).label('listings_processed'),
                func.avg(ScrapingSession.execution_time_seconds).label('avg_time')
            )
            .where(ScrapingSession.started_at >= cutoff_date)
            .group_by(ScrapingSession.platform)
        )
        platform_stats = {
            row.platform: {
                "sessions": row.sessions,
                "listings_processed": row.listings_processed or 0,
                "avg_execution_time": float(row.avg_time) if row.avg_time else None
            }
            for row in platform_result
        }
        
        return ScrapingStats(
            total_sessions=total_sessions or 0,
            successful_sessions=successful_sessions or 0,
            failed_sessions=failed_sessions or 0,
            total_listings_found=listings_data.total_found or 0,
            total_listings_processed=listings_data.total_processed or 0,
            avg_execution_time=float(avg_execution_time) if avg_execution_time else None,
            platform_stats=platform_stats
        )
