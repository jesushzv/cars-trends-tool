"""
Scrapers management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models.scraping_session import ScrapingSession
from app.schemas.scraping_session import ScrapingSessionResponse, ScrapingSessionCreate
from app.services.scraper_service import ScraperService
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/trigger")
async def trigger_scraping(
    platform: Optional[str] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger scraping for all platforms or a specific platform"""
    if platform and platform not in ['facebook', 'craigslist', 'mercadolibre']:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    scraper_service = ScraperService(db)
    
    # Start scraping in background
    if platform:
        background_tasks.add_task(scraper_service.scrape_platform, platform)
        message = f"Scraping triggered for {platform}"
    else:
        background_tasks.add_task(scraper_service.scrape_all_platforms)
        message = "Scraping triggered for all platforms"
    
    return {"message": message, "status": "started"}


@router.get("/status", response_model=List[ScrapingSessionResponse])
async def get_scraping_status(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current scraping status"""
    scraper_service = ScraperService(db)
    
    sessions = await scraper_service.get_recent_sessions(limit=limit)
    return sessions


@router.get("/history", response_model=List[ScrapingSessionResponse])
async def get_scraping_history(
    platform: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scraping history"""
    if platform and platform not in ['facebook', 'craigslist', 'mercadolibre']:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    scraper_service = ScraperService(db)
    
    sessions = await scraper_service.get_scraping_history(
        platform=platform,
        limit=limit
    )
    return sessions


@router.get("/stats")
async def get_scraping_stats(
    days_back: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scraping statistics"""
    scraper_service = ScraperService(db)
    
    stats = await scraper_service.get_scraping_stats(days_back=days_back)
    return stats
