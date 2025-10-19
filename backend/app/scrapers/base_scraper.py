"""
Base scraper class for all platform scrapers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging
import asyncio
import random
from urllib.parse import urljoin, urlparse

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base scraper class for all platform scrapers"""
    
    def __init__(self, db: AsyncSession, platform: str):
        self.db = db
        self.platform = platform
        self.base_url = ""
        self.session = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]
    
    @abstractmethod
    async def scrape(self) -> Dict[str, Any]:
        """Main scraping method - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def extract_car_info(self, listing_data: Any) -> Dict[str, Any]:
        """Extract car information from listing data"""
        pass
    
    @abstractmethod
    def extract_engagement(self, listing_data: Any) -> Dict[str, int]:
        """Extract engagement metrics from listing data"""
        pass
    
    def normalize_car_model(self, make: str, model: str) -> tuple:
        """Normalize car make/model names"""
        if not make or not model:
            return make, model
        
        # Convert to lowercase and strip whitespace
        make = make.lower().strip()
        model = model.lower().strip()
        
        # Common normalizations
        normalizations = {
            'chevrolet': 'chevy',
            'mercedes-benz': 'mercedes',
            'mercedes benz': 'mercedes',
            'volkswagen': 'vw',
            'land rover': 'landrover',
            'alfa romeo': 'alfaromeo'
        }
        
        for old, new in normalizations.items():
            if old in make:
                make = make.replace(old, new)
        
        return make, model
    
    async def delay(self):
        """Add random delay between requests"""
        delay = random.uniform(settings.SCRAPING_DELAY_MIN, settings.SCRAPING_DELAY_MAX)
        await asyncio.sleep(delay)
    
    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(self.user_agents)
    
    def clean_price(self, price_text: str) -> Optional[float]:
        """Clean and extract price from text"""
        if not price_text:
            return None
        
        # Remove common currency symbols and text
        import re
        price_text = re.sub(r'[^\d.,]', '', price_text)
        price_text = price_text.replace(',', '')
        
        try:
            return float(price_text)
        except ValueError:
            return None
    
    def clean_mileage(self, mileage_text: str) -> Optional[int]:
        """Clean and extract mileage from text"""
        if not mileage_text:
            return None
        
        import re
        # Extract numbers from mileage text
        numbers = re.findall(r'\d+', mileage_text.replace(',', ''))
        if numbers:
            try:
                return int(numbers[0])
            except ValueError:
                return None
        return None
    
    def extract_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        if not text:
            return None
        
        import re
        # Look for 4-digit years between 1900 and current year + 1
        current_year = datetime.now().year
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
        
        for year in years:
            year_int = int(year)
            if 1900 <= year_int <= current_year + 1:
                return year_int
        
        return None
    
    def is_valid_listing(self, listing_data: Dict[str, Any]) -> bool:
        """Check if listing data is valid"""
        required_fields = ['title', 'url']
        return all(field in listing_data and listing_data[field] for field in required_fields)
    
    async def save_listing(self, listing_data: Dict[str, Any]) -> bool:
        """Save listing to database"""
        try:
            from app.models.listing import Listing
            from sqlalchemy import select
            
            # Check if listing already exists
            result = await self.db.execute(
                select(Listing).where(
                    Listing.platform == self.platform,
                    Listing.external_id == listing_data.get('external_id')
                )
            )
            existing_listing = result.scalar_one_or_none()
            
            if existing_listing:
                # Update existing listing
                for key, value in listing_data.items():
                    if hasattr(existing_listing, key) and value is not None:
                        setattr(existing_listing, key, value)
                existing_listing.scraped_at = datetime.utcnow()
                await self.db.commit()
                return False  # Updated, not new
            else:
                # Create new listing
                listing = Listing(
                    platform=self.platform,
                    **listing_data
                )
                self.db.add(listing)
                await self.db.commit()
                return True  # New listing
            
        except Exception as e:
            logger.error(f"Error saving listing: {e}")
            await self.db.rollback()
            return False
