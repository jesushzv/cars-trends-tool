"""
Scheduler Service for automated scraping and snapshots
Phase 14: Scheduling
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler = None
_scheduler_started = False


def _job_wrapper(job_func, job_name: str):
    """Wrapper to add logging and error handling to jobs"""
    def wrapper():
        logger.info(f"Starting job: {job_name}")
        start_time = datetime.now()
        try:
            result = job_func()
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Job '{job_name}' completed successfully in {duration:.2f}s: {result}")
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Job '{job_name}' failed after {duration:.2f}s: {str(e)}")
            raise
    return wrapper


def _scrape_craigslist_job():
    """Job to scrape Craigslist"""
    from scrapers.craigslist import scrape_craigslist_tijuana
    from db_service import save_listings
    
    listings = scrape_craigslist_tijuana(max_results=50)
    saved, duplicates = save_listings(listings)
    return f"Craigslist: {saved} saved, {duplicates} duplicates"


def _scrape_mercadolibre_job():
    """Job to scrape Mercado Libre"""
    from scrapers.mercadolibre import scrape_mercadolibre_tijuana
    from db_service import save_listings
    
    listings = scrape_mercadolibre_tijuana(max_results=50)
    saved, duplicates = save_listings(listings)
    return f"Mercado Libre: {saved} saved, {duplicates} duplicates"


def _scrape_facebook_job():
    """Job to scrape Facebook Marketplace"""
    from scrapers.facebook_marketplace import scrape_facebook_tijuana
    from db_service import save_listings
    
    try:
        listings = scrape_facebook_tijuana(max_results=50, headless=True)
        saved, duplicates = save_listings(listings)
        return f"Facebook: {saved} saved, {duplicates} duplicates"
    except Exception as e:
        # Facebook may fail if cookies expired - ALERT as per Phase 19.6
        _facebook_failure_alert(str(e))
        return f"Facebook: Failed - {str(e)}"


def _create_snapshot_job():
    """Job to create daily snapshot"""
    from services.trends_service import create_daily_snapshot
    
    result = create_daily_snapshot()
    return f"Snapshot: {result['snapshots_created']} created, {result['snapshots_updated']} updated"


def _cleanup_job():
    """Job to cleanup old data"""
    from services.cleanup_service import cleanup_all
    
    result = cleanup_all()
    return f"Cleanup: {result['total_deleted']} items deleted (listings: {result['listings']['deleted_count']}, snapshots: {result['snapshots']['deleted_count']})"


def _facebook_failure_alert(error_msg: str):
    """Alert about Facebook scraping failure (Phase 19.6 requirement)"""
    logger.error("=" * 70)
    logger.error("⚠️  ALERT: FACEBOOK SCRAPING FAILED")
    logger.error("=" * 70)
    logger.error(f"Error: {error_msg}")
    logger.error("Possible causes:")
    logger.error("  1. Facebook cookies expired")
    logger.error("  2. Facebook changed their HTML structure")
    logger.error("  3. IP temporarily blocked")
    logger.error("")
    logger.error("Action required:")
    logger.error("  - Check backend/HOW_TO_GET_FB_COOKIES.md")
    logger.error("  - Export fresh cookies if needed")
    logger.error("  - Replace backend/fb_cookies.json")
    logger.error("=" * 70)


def initialize_scheduler(auto_start: bool = True) -> BackgroundScheduler:
    """
    Initialize the scheduler with all jobs
    
    Phase 19.6: Now includes cleanup job and auto-starts by default
    
    Jobs scheduled:
    - Craigslist scraping: Daily at 2:00 AM
    - Mercado Libre scraping: Daily at 3:00 AM
    - Facebook scraping: Daily at 4:00 AM
    - Daily snapshot: Daily at 5:00 AM (after all scraping)
    - Data cleanup: Daily at 6:00 AM (after snapshot)
    
    Args:
        auto_start: If True, automatically start scheduler after initialization
    
    Returns:
        Configured BackgroundScheduler instance
    """
    global _scheduler, _scheduler_started
    
    if _scheduler is not None:
        logger.warning("Scheduler already initialized")
        return _scheduler
    
    logger.info("Initializing scheduler...")
    scheduler = BackgroundScheduler(timezone='America/Tijuana')
    
    # Add Craigslist scraping job - Daily at 2:00 AM
    scheduler.add_job(
        _job_wrapper(_scrape_craigslist_job, "Scrape Craigslist"),
        trigger=CronTrigger(hour=2, minute=0),
        id='scrape_craigslist',
        name='Scrape Craigslist Daily',
        replace_existing=True
    )
    logger.info("Added job: Scrape Craigslist (daily at 2:00 AM)")
    
    # Add Mercado Libre scraping job - Daily at 3:00 AM
    scheduler.add_job(
        _job_wrapper(_scrape_mercadolibre_job, "Scrape Mercado Libre"),
        trigger=CronTrigger(hour=3, minute=0),
        id='scrape_mercadolibre',
        name='Scrape Mercado Libre Daily',
        replace_existing=True
    )
    logger.info("Added job: Scrape Mercado Libre (daily at 3:00 AM)")
    
    # Add Facebook scraping job - Daily at 4:00 AM
    scheduler.add_job(
        _job_wrapper(_scrape_facebook_job, "Scrape Facebook"),
        trigger=CronTrigger(hour=4, minute=0),
        id='scrape_facebook',
        name='Scrape Facebook Marketplace Daily',
        replace_existing=True
    )
    logger.info("Added job: Scrape Facebook (daily at 4:00 AM)")
    
    # Add daily snapshot job - Daily at 5:00 AM (after scraping)
    scheduler.add_job(
        _job_wrapper(_create_snapshot_job, "Create Daily Snapshot"),
        trigger=CronTrigger(hour=5, minute=0),
        id='daily_snapshot',
        name='Create Daily Snapshot',
        replace_existing=True
    )
    logger.info("Added job: Create Daily Snapshot (daily at 5:00 AM)")
    
    # Add cleanup job - Daily at 6:00 AM (Phase 19.6: after snapshot)
    scheduler.add_job(
        _job_wrapper(_cleanup_job, "Cleanup Old Data"),
        trigger=CronTrigger(hour=6, minute=0),
        id='cleanup_data',
        name='Cleanup Old Data Daily',
        replace_existing=True
    )
    logger.info("Added job: Cleanup Old Data (daily at 6:00 AM)")
    
    _scheduler = scheduler
    logger.info("Scheduler initialized with 5 jobs")
    
    # Auto-start if requested (Phase 19.6: default behavior)
    if auto_start:
        scheduler.start()
        _scheduler_started = True
        logger.info("✅ Scheduler auto-started")
    
    return scheduler


def start_scheduler():
    """
    Start the scheduler
    
    Returns:
        Dict with status information
    """
    global _scheduler, _scheduler_started
    
    if _scheduler is None:
        initialize_scheduler()
    
    if _scheduler_started:
        return {
            'status': 'already_running',
            'message': 'Scheduler is already running'
        }
    
    _scheduler.start()
    _scheduler_started = True
    logger.info("Scheduler started")
    
    return {
        'status': 'started',
        'message': 'Scheduler started successfully',
        'jobs': get_jobs()
    }


def stop_scheduler():
    """
    Stop the scheduler
    
    Returns:
        Dict with status information
    """
    global _scheduler, _scheduler_started
    
    if _scheduler is None or not _scheduler_started:
        return {
            'status': 'not_running',
            'message': 'Scheduler is not running'
        }
    
    _scheduler.shutdown(wait=False)
    _scheduler_started = False
    logger.info("Scheduler stopped")
    
    return {
        'status': 'stopped',
        'message': 'Scheduler stopped successfully'
    }


def get_scheduler_status() -> Dict:
    """
    Get current scheduler status
    
    Returns:
        Dict with scheduler status and job information
    """
    global _scheduler, _scheduler_started
    
    if _scheduler is None:
        return {
            'running': False,
            'message': 'Scheduler not initialized',
            'jobs': []
        }
    
    return {
        'running': _scheduler_started,
        'message': 'Scheduler is running' if _scheduler_started else 'Scheduler is stopped',
        'jobs': get_jobs()
    }


def get_jobs() -> List[Dict]:
    """
    Get list of all scheduled jobs
    
    Returns:
        List of job information dicts
    """
    global _scheduler
    
    if _scheduler is None:
        return []
    
    jobs = []
    for job in _scheduler.get_jobs():
        next_run = getattr(job, 'next_run_time', None)
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': next_run.isoformat() if next_run else None,
            'trigger': str(job.trigger)
        })
    
    return jobs


def trigger_job_now(job_id: str) -> Dict:
    """
    Manually trigger a specific job to run immediately
    
    Args:
        job_id: Job ID to trigger ('scrape_craigslist', 'scrape_mercadolibre', 
                'scrape_facebook', or 'daily_snapshot')
    
    Returns:
        Dict with result information
    """
    global _scheduler
    
    if _scheduler is None:
        return {
            'success': False,
            'message': 'Scheduler not initialized'
        }
    
    # Map of job IDs to their functions
    job_functions = {
        'scrape_craigslist': _scrape_craigslist_job,
        'scrape_mercadolibre': _scrape_mercadolibre_job,
        'scrape_facebook': _scrape_facebook_job,
        'daily_snapshot': _create_snapshot_job
    }
    
    if job_id not in job_functions:
        return {
            'success': False,
            'message': f'Unknown job ID: {job_id}',
            'valid_ids': list(job_functions.keys())
        }
    
    try:
        logger.info(f"Manually triggering job: {job_id}")
        result = _job_wrapper(job_functions[job_id], job_id)()
        return {
            'success': True,
            'job_id': job_id,
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'job_id': job_id,
            'error': str(e)
        }


if __name__ == "__main__":
    # Test the scheduler
    print("=" * 80)
    print("Testing Scheduler Service")
    print("=" * 80)
    
    print("\n1. Initializing scheduler...")
    scheduler = initialize_scheduler()
    print(f"   ✓ Scheduler initialized")
    
    print("\n2. Getting job list...")
    jobs = get_jobs()
    print(f"   ✓ Found {len(jobs)} jobs:")
    for job in jobs:
        print(f"      - {job['name']}")
        print(f"        ID: {job['id']}")
        print(f"        Next run: {job['next_run']}")
    
    print("\n3. Getting status...")
    status = get_scheduler_status()
    print(f"   Running: {status['running']}")
    print(f"   Message: {status['message']}")
    
    print("\n4. Starting scheduler...")
    result = start_scheduler()
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    
    print("\n5. Getting status again...")
    status = get_scheduler_status()
    print(f"   Running: {status['running']}")
    
    print("\n6. Stopping scheduler...")
    result = stop_scheduler()
    print(f"   Status: {result['status']}")
    
    print("\n" + "=" * 80)
    print("✅ Scheduler service test complete!")

