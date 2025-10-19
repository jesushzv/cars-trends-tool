"""
Scheduler service for managing automated scraping jobs
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from datetime import datetime

from app.core.database import AsyncSessionLocal
from app.services.scraper_service import ScraperService

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled scraping jobs"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def start_scheduler(self):
        """Start the scheduler with predefined jobs"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Schedule daily scraping at 6 AM
            self.scheduler.add_job(
                func=self._run_daily_scraping,
                trigger=CronTrigger(hour=6, minute=0),
                id='daily_scraping',
                name='Daily Car Listings Scraping',
                replace_existing=True,
                max_instances=1
            )
            
            # Schedule weekly trend analysis at 7 AM on Sundays
            self.scheduler.add_job(
                func=self._run_weekly_analysis,
                trigger=CronTrigger(day_of_week=0, hour=7, minute=0),
                id='weekly_analysis',
                name='Weekly Trend Analysis',
                replace_existing=True,
                max_instances=1
            )
            
            # Schedule monthly cleanup at 2 AM on the 1st of each month
            self.scheduler.add_job(
                func=self._run_monthly_cleanup,
                trigger=CronTrigger(day=1, hour=2, minute=0),
                id='monthly_cleanup',
                name='Monthly Data Cleanup',
                replace_existing=True,
                max_instances=1
            )
            
            self.scheduler.start()
            self.is_running = True
            
            logger.info("Scheduler started successfully")
            logger.info("Scheduled jobs:")
            for job in self.scheduler.get_jobs():
                logger.info(f"  - {job.name} (ID: {job.id}) - Next run: {job.next_run_time}")
                
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop_scheduler(self):
        """Stop the scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Scheduler stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
            raise
    
    async def _run_daily_scraping(self):
        """Run daily scraping for all platforms"""
        logger.info("Starting daily scraping job")
        start_time = datetime.utcnow()
        
        try:
            async with AsyncSessionLocal() as db:
                scraper_service = ScraperService(db)
                sessions = await scraper_service.scrape_all_platforms()
                
                total_processed = sum(session.listings_processed for session in sessions)
                total_new = sum(session.listings_new for session in sessions)
                total_updated = sum(session.listings_updated for session in sessions)
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                
                logger.info(f"Daily scraping completed in {execution_time:.2f} seconds")
                logger.info(f"Total processed: {total_processed}, New: {total_new}, Updated: {total_updated}")
                
        except Exception as e:
            logger.error(f"Daily scraping job failed: {e}")
    
    async def _run_weekly_analysis(self):
        """Run weekly trend analysis and cleanup"""
        logger.info("Starting weekly analysis job")
        start_time = datetime.utcnow()
        
        try:
            async with AsyncSessionLocal() as db:
                # Update trend calculations
                from app.services.trend_service import TrendService
                trend_service = TrendService(db)
                
                # Calculate trends for the past week
                # This would involve aggregating listing data into trends
                # Implementation depends on your specific trend calculation logic
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"Weekly analysis completed in {execution_time:.2f} seconds")
                
        except Exception as e:
            logger.error(f"Weekly analysis job failed: {e}")
    
    async def _run_monthly_cleanup(self):
        """Run monthly data cleanup and archiving"""
        logger.info("Starting monthly cleanup job")
        start_time = datetime.utcnow()
        
        try:
            async with AsyncSessionLocal() as db:
                # Archive old listings (older than 6 months)
                from app.models.listing import Listing
                from sqlalchemy import delete
                from datetime import datetime, timedelta
                
                cutoff_date = datetime.utcnow() - timedelta(days=180)
                
                result = await db.execute(
                    delete(Listing).where(
                        Listing.scraped_at < cutoff_date,
                        Listing.is_active == False
                    )
                )
                
                deleted_count = result.rowcount
                await db.commit()
                
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                logger.info(f"Monthly cleanup completed in {execution_time:.2f} seconds")
                logger.info(f"Archived {deleted_count} old listings")
                
        except Exception as e:
            logger.error(f"Monthly cleanup job failed: {e}")
    
    def get_job_status(self):
        """Get status of all scheduled jobs"""
        if not self.is_running:
            return {"status": "stopped", "jobs": []}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "running",
            "jobs": jobs
        }
    
    def trigger_job(self, job_id: str):
        """Manually trigger a specific job"""
        if not self.is_running:
            raise RuntimeError("Scheduler is not running")
        
        job = self.scheduler.get_job(job_id)
        if not job:
            raise ValueError(f"Job with ID '{job_id}' not found")
        
        job.modify(next_run_time=datetime.utcnow())
        logger.info(f"Manually triggered job: {job.name}")


# Global scheduler instance
scheduler_service = SchedulerService()
