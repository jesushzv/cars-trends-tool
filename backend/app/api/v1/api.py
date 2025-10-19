"""
API v1 router configuration
"""

from fastapi import APIRouter
from app.api.v1.endpoints import listings, trends, analytics, auth, scrapers

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(trends.router, prefix="/trends", tags=["trends"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(scrapers.router, prefix="/scrapers", tags=["scrapers"])
