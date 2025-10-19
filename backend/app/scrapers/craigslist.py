"""
Craigslist scraper for Tijuana, Mexico
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urljoin, urlencode, parse_qs, urlparse

from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class CraigslistScraper(BaseScraper):
    """Craigslist scraper for Tijuana, Mexico"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, "craigslist")
        self.base_url = "https://tijuana.craigslist.org"
        self.search_url = "https://tijuana.craigslist.org/search/cta"
        self.session = None
    
    async def scrape(self) -> Dict[str, Any]:
        """Scrape Craigslist for car listings"""
        result = {
            'listings_found': 0,
            'listings_processed': 0,
            'listings_new': 0,
            'listings_updated': 0,
            'errors': []
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                self.session = session
                
                # Scrape listings
                listings = await self._scrape_listings()
                result['listings_found'] = len(listings)
                
                # Process each listing
                for listing_data in listings:
                    try:
                        if self.is_valid_listing(listing_data):
                            is_new = await self.save_listing(listing_data)
                            result['listings_processed'] += 1
                            if is_new:
                                result['listings_new'] += 1
                            else:
                                result['listings_updated'] += 1
                        await self.delay()
                    except Exception as e:
                        logger.error(f"Error processing listing: {e}")
                        result['errors'].append(str(e))
                
        except Exception as e:
            logger.error(f"Craigslist scraping failed: {e}")
            result['errors'].append(str(e))
        
        return result
    
    async def _scrape_listings(self) -> List[Dict[str, Any]]:
        """Scrape all visible listings"""
        listings = []
        
        try:
            # Build search URL with parameters
            params = {
                'query': 'car',
                'sort': 'date',
                'postedToday': '1'  # Only today's listings
            }
            
            search_url = f"{self.search_url}?{urlencode(params)}"
            
            async with self.session.get(search_url, headers={'User-Agent': self.get_random_user_agent()}) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find all listing links
                    listing_links = soup.find_all('a', class_='result-title')
                    
                    for link in listing_links[:50]:  # Limit to 50 listings per run
                        try:
                            href = link.get('href')
                            if href:
                                full_url = urljoin(self.base_url, href)
                                listing_data = await self._scrape_listing_detail(full_url)
                                if listing_data:
                                    listings.append(listing_data)
                                await self.delay()
                        except Exception as e:
                            logger.error(f"Error scraping listing link: {e}")
                            continue
                else:
                    logger.error(f"Failed to fetch Craigslist search page: {response.status}")
        
        except Exception as e:
            logger.error(f"Error scraping Craigslist listings: {e}")
        
        return listings
    
    async def _scrape_listing_detail(self, listing_url: str) -> Optional[Dict[str, Any]]:
        """Scrape detailed information from a listing"""
        try:
            async with self.session.get(listing_url, headers={'User-Agent': self.get_random_user_agent()}) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract listing data
                    listing_data = {
                        'external_id': self._extract_listing_id(listing_url),
                        'url': listing_url,
                        'title': self._extract_title(soup),
                        'description': self._extract_description(soup),
                        'price': self._extract_price(soup),
                        'images': self._extract_images(soup),
                        'location': self._extract_location(soup),
                        'posted_date': self._extract_posted_date(soup),
                        'views': 0,  # Craigslist doesn't show view counts
                        'likes': 0,  # Craigslist doesn't have likes
                        'comments': 0,  # Craigslist doesn't have comments
                        'saves': 0,  # Craigslist doesn't have saves
                        'shares': 0  # Craigslist doesn't have shares
                    }
                    
                    # Extract car-specific information
                    car_info = self._extract_car_info(soup, listing_data['title'], listing_data['description'])
                    listing_data.update(car_info)
                    
                    return listing_data
                else:
                    logger.error(f"Failed to fetch listing detail: {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error scraping listing detail: {e}")
            return None
    
    def _extract_listing_id(self, url: str) -> str:
        """Extract listing ID from URL"""
        match = re.search(r'/(\d+)\.html', url)
        return match.group(1) if match else url.split('/')[-1].replace('.html', '')
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract listing title"""
        title_elem = soup.find('span', {'id': 'titletextonly'})
        return title_elem.get_text().strip() if title_elem else ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract listing description"""
        desc_elem = soup.find('section', {'id': 'postingbody'})
        if desc_elem:
            # Remove the "show contact info" link
            contact_link = desc_elem.find('a', {'class': 'showcontact'})
            if contact_link:
                contact_link.decompose()
            return desc_elem.get_text().strip()
        return ""
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract listing price"""
        price_elem = soup.find('span', {'class': 'price'})
        if price_elem:
            price_text = price_elem.get_text().strip()
            return self.clean_price(price_text)
        return None
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract listing images"""
        images = []
        img_elements = soup.find_all('img', {'class': 'slide'})
        for img in img_elements:
            src = img.get('src')
            if src:
                images.append(src)
        return images
    
    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract listing location"""
        location_elem = soup.find('div', {'class': 'mapaddress'})
        if location_elem:
            return location_elem.get_text().strip()
        
        # Try alternative location selectors
        location_elem = soup.find('span', {'class': 'postingtitletext'})
        if location_elem:
            # Extract location from title (usually in parentheses)
            title_text = location_elem.get_text()
            match = re.search(r'\(([^)]+)\)', title_text)
            if match:
                return match.group(1)
        
        return "Tijuana, Mexico"  # Default location
    
    def _extract_posted_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract posted date"""
        date_elem = soup.find('time', {'class': 'date'})
        if date_elem:
            return date_elem.get('datetime')
        
        # Try alternative date selectors
        date_elem = soup.find('p', {'class': 'postinginfo'})
        if date_elem:
            date_text = date_elem.get_text()
            if 'posted:' in date_text.lower():
                return date_text.split('posted:')[-1].strip()
        
        return None
    
    def _extract_car_info(self, soup: BeautifulSoup, title: str, description: str) -> Dict[str, Any]:
        """Extract car-specific information"""
        car_info = {}
        
        try:
            full_text = f"{title} {description}".lower()
            
            # Extract make and model
            make, model = self._extract_make_model(full_text)
            if make:
                car_info['make'] = make
            if model:
                car_info['model'] = model
            
            # Extract year
            year = self.extract_year(full_text)
            if year:
                car_info['year'] = year
            
            # Extract mileage
            mileage = self._extract_mileage(full_text)
            if mileage:
                car_info['mileage'] = mileage
            
            # Extract condition
            condition = self._extract_condition(full_text)
            if condition:
                car_info['condition'] = condition
            
            # Look for car attributes in the posting
            attributes = soup.find_all('p', {'class': 'attrgroup'})
            for attr_group in attributes:
                spans = attr_group.find_all('span')
                for span in spans:
                    text = span.get_text().lower()
                    if 'odometer:' in text:
                        odometer = self.clean_mileage(text.split('odometer:')[-1])
                        if odometer:
                            car_info['mileage'] = odometer
                    elif 'condition:' in text:
                        cond = text.split('condition:')[-1].strip()
                        if cond in ['excellent', 'good', 'fair', 'poor']:
                            car_info['condition'] = cond
            
        except Exception as e:
            logger.error(f"Error extracting car info: {e}")
        
        return car_info
    
    def _extract_make_model(self, text: str) -> tuple:
        """Extract make and model from text"""
        # Common car makes
        makes = [
            'toyota', 'honda', 'nissan', 'ford', 'chevrolet', 'chevy', 'bmw', 'mercedes',
            'audi', 'volkswagen', 'vw', 'hyundai', 'kia', 'mazda', 'subaru', 'lexus',
            'infiniti', 'acura', 'volvo', 'saab', 'jeep', 'dodge', 'chrysler', 'gmc',
            'cadillac', 'lincoln', 'buick', 'pontiac', 'saturn', 'oldsmobile'
        ]
        
        text_lower = text.lower()
        for make in makes:
            if make in text_lower:
                # Try to extract model after make
                make_index = text_lower.find(make)
                after_make = text_lower[make_index + len(make):make_index + len(make) + 20]
                words = after_make.split()
                if words:
                    model = words[0]
                    return make, model
                return make, None
        
        return None, None
    
    def _extract_mileage(self, text: str) -> Optional[int]:
        """Extract mileage from text"""
        import re
        # Look for patterns like "50,000 miles", "50k miles", "50000 km"
        patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:kilometers?|km)',
            r'(\d{1,3}(?:,\d{3})*)\s*k\s*(?:miles?|mi)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_mileage(match.group(1))
        
        return None
    
    def _extract_condition(self, text: str) -> Optional[str]:
        """Extract condition from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['new', 'brand new', '0 miles']):
            return 'new'
        elif any(word in text_lower for word in ['certified', 'cpo', 'certified pre-owned']):
            return 'certified'
        elif any(word in text_lower for word in ['salvage', 'rebuilt', 'totaled']):
            return 'salvage'
        elif any(word in text_lower for word in ['used', 'pre-owned', 'second hand']):
            return 'used'
        
        return 'used'  # Default to used
    
    def extract_car_info(self, listing_data: Any) -> Dict[str, Any]:
        """Extract car information from listing data (implemented from base class)"""
        return listing_data.get('car_info', {})
    
    def extract_engagement(self, listing_data: Any) -> Dict[str, int]:
        """Extract engagement metrics from listing data (implemented from base class)"""
        return {
            'views': listing_data.get('views', 0),
            'likes': listing_data.get('likes', 0),
            'comments': listing_data.get('comments', 0),
            'saves': listing_data.get('saves', 0),
            'shares': listing_data.get('shares', 0)
        }
