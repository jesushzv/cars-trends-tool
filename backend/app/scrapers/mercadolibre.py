"""
Mercado Libre scraper for Tijuana, Mexico
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


class MercadoLibreScraper(BaseScraper):
    """Mercado Libre scraper for Tijuana, Mexico"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, "mercadolibre")
        self.base_url = "https://www.mercadolibre.com.mx"
        self.search_url = "https://autos.mercadolibre.com.mx"
        self.session = None
    
    async def scrape(self) -> Dict[str, Any]:
        """Scrape Mercado Libre for car listings"""
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
            logger.error(f"Mercado Libre scraping failed: {e}")
            result['errors'].append(str(e))
        
        return result
    
    async def _scrape_listings(self) -> List[Dict[str, Any]]:
        """Scrape all visible listings"""
        listings = []
        
        try:
            # Build search URL with parameters
            params = {
                'q': 'carros',
                'sort': 'relevance',
                'state': 'BCN',  # Baja California
                'city': 'Tijuana'
            }
            
            search_url = f"{self.search_url}?{urlencode(params)}"
            
            async with self.session.get(search_url, headers={'User-Agent': self.get_random_user_agent()}) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find all listing links
                    listing_links = soup.find_all('a', {'class': 'ui-search-item__group__element'})
                    
                    for link in listing_links[:50]:  # Limit to 50 listings per run
                        try:
                            href = link.get('href')
                            if href:
                                listing_data = await self._scrape_listing_detail(href)
                                if listing_data:
                                    listings.append(listing_data)
                                await self.delay()
                        except Exception as e:
                            logger.error(f"Error scraping listing link: {e}")
                            continue
                else:
                    logger.error(f"Failed to fetch Mercado Libre search page: {response.status}")
        
        except Exception as e:
            logger.error(f"Error scraping Mercado Libre listings: {e}")
        
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
                        'views': self._extract_views(soup),
                        'likes': self._extract_likes(soup),
                        'comments': self._extract_comments(soup),
                        'saves': self._extract_saves(soup),
                        'shares': self._extract_shares(soup)
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
        match = re.search(r'MLM-(\d+)', url)
        return match.group(1) if match else url.split('/')[-1]
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract listing title"""
        title_elem = soup.find('h1', {'class': 'ui-pdp-title'})
        return title_elem.get_text().strip() if title_elem else ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract listing description"""
        desc_elem = soup.find('p', {'class': 'ui-pdp-description__content'})
        return desc_elem.get_text().strip() if desc_elem else ""
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract listing price"""
        price_elem = soup.find('span', {'class': 'andes-money-amount__fraction'})
        if price_elem:
            price_text = price_elem.get_text().strip()
            return self.clean_price(price_text)
        return None
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract listing images"""
        images = []
        img_elements = soup.find_all('img', {'class': 'ui-pdp-image'})
        for img in img_elements:
            src = img.get('src')
            if src:
                images.append(src)
        return images
    
    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract listing location"""
        location_elem = soup.find('p', {'class': 'ui-pdp-location'})
        if location_elem:
            return location_elem.get_text().strip()
        return "Tijuana, Mexico"  # Default location
    
    def _extract_posted_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract posted date"""
        date_elem = soup.find('span', {'class': 'ui-pdp-subtitle'})
        if date_elem:
            date_text = date_elem.get_text()
            if 'publicado' in date_text.lower():
                return date_text.split('publicado')[-1].strip()
        return None
    
    def _extract_views(self, soup: BeautifulSoup) -> int:
        """Extract view count"""
        views_elem = soup.find('span', {'class': 'ui-pdp-subtitle'})
        if views_elem:
            views_text = views_elem.get_text()
            if 'veces' in views_text.lower():
                match = re.search(r'(\d+)\s*veces', views_text)
                if match:
                    return int(match.group(1))
        return 0
    
    def _extract_likes(self, soup: BeautifulSoup) -> int:
        """Extract like count"""
        # Mercado Libre doesn't show like counts publicly
        return 0
    
    def _extract_comments(self, soup: BeautifulSoup) -> int:
        """Extract comment count"""
        # Mercado Libre doesn't show comment counts publicly
        return 0
    
    def _extract_saves(self, soup: BeautifulSoup) -> int:
        """Extract save count"""
        # Mercado Libre doesn't show save counts publicly
        return 0
    
    def _extract_shares(self, soup: BeautifulSoup) -> int:
        """Extract share count"""
        # Mercado Libre doesn't show share counts publicly
        return 0
    
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
            attributes = soup.find_all('tr', {'class': 'andes-table__row'})
            for attr_row in attributes:
                cells = attr_row.find_all('td')
                if len(cells) >= 2:
                    key = cells[0].get_text().lower().strip()
                    value = cells[1].get_text().strip()
                    
                    if 'kilometraje' in key or 'km' in key:
                        odometer = self.clean_mileage(value)
                        if odometer:
                            car_info['mileage'] = odometer
                    elif 'año' in key or 'modelo' in key:
                        year = self.extract_year(value)
                        if year:
                            car_info['year'] = year
                    elif 'marca' in key:
                        car_info['make'] = value.lower()
                    elif 'modelo' in key:
                        car_info['model'] = value.lower()
                    elif 'condición' in key:
                        if value.lower() in ['nuevo', 'usado', 'seminuevo']:
                            car_info['condition'] = value.lower()
            
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
        # Look for patterns like "50,000 km", "50k km", "50000 kilómetros"
        patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilómetros?)',
            r'(\d{1,3}(?:,\d{3})*)\s*k\s*(?:km|kilómetros?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self.clean_mileage(match.group(1))
        
        return None
    
    def _extract_condition(self, text: str) -> Optional[str]:
        """Extract condition from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['nuevo', 'new', '0 km']):
            return 'new'
        elif any(word in text_lower for word in ['certificado', 'certified', 'seminuevo']):
            return 'certified'
        elif any(word in text_lower for word in ['salvage', 'reconstruido', 'totalizado']):
            return 'salvage'
        elif any(word in text_lower for word in ['usado', 'used', 'segunda mano']):
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
