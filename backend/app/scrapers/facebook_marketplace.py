"""
Facebook Marketplace scraper
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from playwright.async_api import async_playwright, Browser, Page
import logging
import re
from urllib.parse import urljoin, parse_qs, urlparse

from app.scrapers.base_scraper import BaseScraper
from app.core.config import settings

logger = logging.getLogger(__name__)


class FacebookMarketplaceScraper(BaseScraper):
    """Facebook Marketplace scraper for Tijuana, Mexico"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, "facebook")
        self.base_url = "https://www.facebook.com/marketplace"
        self.search_url = "https://www.facebook.com/marketplace/tijuana/search"
        self.browser = None
        self.page = None
    
    async def scrape(self) -> Dict[str, Any]:
        """Scrape Facebook Marketplace for car listings"""
        result = {
            'listings_found': 0,
            'listings_processed': 0,
            'listings_new': 0,
            'listings_updated': 0,
            'errors': []
        }
        
        try:
            async with async_playwright() as p:
                # Launch browser
                self.browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )
                
                # Create new page
                self.page = await self.browser.new_page()
                await self.page.set_extra_http_headers({
                    'User-Agent': self.get_random_user_agent()
                })
                
                # Navigate to marketplace
                await self.page.goto(self.search_url, wait_until='networkidle')
                await self.delay()
                
                # Search for cars in Tijuana
                await self._search_cars()
                
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
            logger.error(f"Facebook scraping failed: {e}")
            result['errors'].append(str(e))
        
        finally:
            if self.browser:
                await self.browser.close()
        
        return result
    
    async def _search_cars(self):
        """Search for cars in the marketplace"""
        try:
            # Click on Vehicles category
            vehicles_selector = '[data-testid="marketplace-category-vehicles"]'
            await self.page.wait_for_selector(vehicles_selector, timeout=10000)
            await self.page.click(vehicles_selector)
            await self.delay()
            
            # Set location to Tijuana if not already set
            location_selector = '[data-testid="marketplace-location-picker"]'
            if await self.page.locator(location_selector).count() > 0:
                await self.page.click(location_selector)
                await self.delay()
                
                # Type Tijuana
                location_input = '[data-testid="location-picker-input"]'
                await self.page.fill(location_input, "Tijuana, Mexico")
                await self.delay()
                
                # Select first result
                first_result = '[data-testid="location-picker-results"] > div:first-child'
                await self.page.click(first_result)
                await self.delay()
            
        except Exception as e:
            logger.error(f"Error setting up search: {e}")
    
    async def _scrape_listings(self) -> List[Dict[str, Any]]:
        """Scrape all visible listings"""
        listings = []
        
        try:
            # Wait for listings to load
            await self.page.wait_for_selector('[data-testid="marketplace-search-results"]', timeout=10000)
            
            # Scroll to load more listings
            await self._scroll_to_load_more()
            
            # Get all listing links
            listing_links = await self.page.query_selector_all('a[href*="/marketplace/item/"]')
            
            for link in listing_links[:50]:  # Limit to 50 listings per run
                try:
                    href = await link.get_attribute('href')
                    if href:
                        listing_data = await self._scrape_listing_detail(href)
                        if listing_data:
                            listings.append(listing_data)
                        await self.delay()
                except Exception as e:
                    logger.error(f"Error scraping listing link: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping listings: {e}")
        
        return listings
    
    async def _scroll_to_load_more(self):
        """Scroll to load more listings"""
        try:
            for _ in range(3):  # Scroll 3 times
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await self.delay()
                await self.page.wait_for_timeout(2000)
        except Exception as e:
            logger.error(f"Error scrolling: {e}")
    
    async def _scrape_listing_detail(self, listing_url: str) -> Optional[Dict[str, Any]]:
        """Scrape detailed information from a listing"""
        try:
            # Navigate to listing
            full_url = urljoin(self.base_url, listing_url)
            await self.page.goto(full_url, wait_until='networkidle')
            await self.delay()
            
            # Extract listing data
            listing_data = {
                'external_id': self._extract_listing_id(listing_url),
                'url': full_url,
                'title': await self._extract_title(),
                'description': await self._extract_description(),
                'price': await self._extract_price(),
                'images': await self._extract_images(),
                'location': await self._extract_location(),
                'posted_date': await self._extract_posted_date(),
                'views': await self._extract_views(),
                'likes': await self._extract_likes(),
                'comments': await self._extract_comments(),
                'saves': await self._extract_saves(),
                'shares': await self._extract_shares()
            }
            
            # Extract car-specific information
            car_info = await self._extract_car_info()
            listing_data.update(car_info)
            
            return listing_data
            
        except Exception as e:
            logger.error(f"Error scraping listing detail: {e}")
            return None
    
    def _extract_listing_id(self, url: str) -> str:
        """Extract listing ID from URL"""
        match = re.search(r'/marketplace/item/(\d+)', url)
        return match.group(1) if match else url.split('/')[-1]
    
    async def _extract_title(self) -> str:
        """Extract listing title"""
        try:
            title_selector = '[data-testid="marketplace-listing-title"]'
            title_element = await self.page.query_selector(title_selector)
            return await title_element.inner_text() if title_element else ""
        except:
            return ""
    
    async def _extract_description(self) -> str:
        """Extract listing description"""
        try:
            desc_selector = '[data-testid="marketplace-listing-description"]'
            desc_element = await self.page.query_selector(desc_selector)
            return await desc_element.inner_text() if desc_element else ""
        except:
            return ""
    
    async def _extract_price(self) -> Optional[float]:
        """Extract listing price"""
        try:
            price_selector = '[data-testid="marketplace-listing-price"]'
            price_element = await self.page.query_selector(price_selector)
            if price_element:
                price_text = await price_element.inner_text()
                return self.clean_price(price_text)
        except:
            pass
        return None
    
    async def _extract_images(self) -> List[str]:
        """Extract listing images"""
        try:
            image_selector = '[data-testid="marketplace-listing-image"] img'
            image_elements = await self.page.query_selector_all(image_selector)
            images = []
            for img in image_elements:
                src = await img.get_attribute('src')
                if src:
                    images.append(src)
            return images
        except:
            return []
    
    async def _extract_location(self) -> str:
        """Extract listing location"""
        try:
            location_selector = '[data-testid="marketplace-listing-location"]'
            location_element = await self.page.query_selector(location_selector)
            return await location_element.inner_text() if location_element else ""
        except:
            return ""
    
    async def _extract_posted_date(self) -> Optional[str]:
        """Extract posted date"""
        try:
            date_selector = '[data-testid="marketplace-listing-date"]'
            date_element = await self.page.query_selector(date_selector)
            if date_element:
                return await date_element.inner_text()
        except:
            pass
        return None
    
    async def _extract_views(self) -> int:
        """Extract view count"""
        # Facebook doesn't show view counts publicly
        return 0
    
    async def _extract_likes(self) -> int:
        """Extract like count"""
        try:
            like_selector = '[data-testid="marketplace-listing-likes"]'
            like_element = await self.page.query_selector(like_selector)
            if like_element:
                like_text = await like_element.inner_text()
                return int(re.findall(r'\d+', like_text)[0]) if re.findall(r'\d+', like_text) else 0
        except:
            pass
        return 0
    
    async def _extract_comments(self) -> int:
        """Extract comment count"""
        try:
            comment_selector = '[data-testid="marketplace-listing-comments"]'
            comment_element = await self.page.query_selector(comment_selector)
            if comment_element:
                comment_text = await comment_element.inner_text()
                return int(re.findall(r'\d+', comment_text)[0]) if re.findall(r'\d+', comment_text) else 0
        except:
            pass
        return 0
    
    async def _extract_saves(self) -> int:
        """Extract save count"""
        # Facebook doesn't show save counts publicly
        return 0
    
    async def _extract_shares(self) -> int:
        """Extract share count"""
        try:
            share_selector = '[data-testid="marketplace-listing-shares"]'
            share_element = await self.page.query_selector(share_selector)
            if share_element:
                share_text = await share_element.inner_text()
                return int(re.findall(r'\d+', share_text)[0]) if re.findall(r'\d+', share_text) else 0
        except:
            pass
        return 0
    
    async def _extract_car_info(self) -> Dict[str, Any]:
        """Extract car-specific information"""
        car_info = {}
        
        try:
            # Look for car details in description or title
            title = await self._extract_title()
            description = await self._extract_description()
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
