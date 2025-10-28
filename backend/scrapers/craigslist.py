"""
Craigslist Scraper for Tijuana Car Listings
Phase 1: Basic scraper extracting title, price, url
Phase 4: Enhanced with car-specific fields and odometer extraction
Phase 7: Added data normalization
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import re
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.parser import parse_listing_title
from utils.normalizer import normalize_car_data


def scrape_craigslist_tijuana(max_results: int = 10, fetch_details: bool = True) -> List[Dict]:
    """
    Scrape car listings from Craigslist Tijuana
    
    Args:
        max_results: Maximum number of listings to return
        fetch_details: If True, fetch detailed info (odometer, make/model) from each listing page
        
    Returns:
        List of dicts with keys: title, price, url, make, model, year, mileage
        Example: [
            {
                'title': '2016 Renault Koleos',
                'price': 12000.0,
                'url': 'https://tijuana.craigslist.org/...',
                'make': 'Renault',
                'model': 'Koleos',
                'year': 2016,
                'mileage': 88000  # in kilometers for Mexico listings
            }
        ]
    """
    listings = []
    
    try:
        # Craigslist Tijuana cars+trucks search URL
        url = "https://tijuana.craigslist.org/search/cta"
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Make request
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all listing items
        # Craigslist uses <li class="cl-static-search-result"> for each listing
        items = soup.find_all('li', class_='cl-static-search-result', limit=max_results)
        
        print(f"Found {len(items)} listings on search page, processing...")
        
        for idx, item in enumerate(items, 1):
            try:
                # Extract title
                title_elem = item.find('div', class_='title')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                # Extract URL
                link_elem = item.find('a')
                if not link_elem or not link_elem.get('href'):
                    continue
                listing_url = link_elem['href']
                
                # Make URL absolute if needed
                if not listing_url.startswith('http'):
                    listing_url = 'https://tijuana.craigslist.org' + listing_url
                
                # Extract price
                price_elem = item.find('div', class_='price')
                price = None
                if price_elem:
                    price = _parse_price(price_elem.get_text(strip=True))
                
                # First, parse title for car details
                car_info = parse_listing_title(title)
                
                # If fetch_details is True, get more accurate data from the listing page
                if fetch_details:
                    print(f"  [{idx}/{len(items)}] Fetching details for: {title[:50]}...")
                    detail_info = _extract_listing_details(listing_url)
                    
                    # Use detail_info to override/supplement car_info
                    # Prefer detail page data when available
                    if detail_info.get('make'):
                        car_info['make'] = detail_info['make']
                    if detail_info.get('model'):
                        car_info['model'] = detail_info['model']
                    if detail_info.get('year'):
                        car_info['year'] = detail_info['year']
                    if detail_info.get('mileage'):
                        car_info['mileage'] = detail_info['mileage']
                
                # Normalize the car data (Phase 7)
                normalized = normalize_car_data(
                    make=car_info.get('make'),
                    model=car_info.get('model'),
                    year=car_info.get('year'),
                    mileage=car_info.get('mileage')
                )
                
                listings.append({
                    'title': title,
                    'price': price,
                    'url': listing_url,
                    'make': normalized.get('make'),
                    'model': normalized.get('model'),
                    'year': normalized.get('year'),
                    'mileage': normalized.get('mileage')
                })
                
            except Exception as e:
                # Skip individual listing errors
                print(f"  [ERROR] Failed to process listing: {e}")
                continue
        
        # Add small delay to be respectful
        time.sleep(1)
        
    except Exception as e:
        # Return empty list on error, don't crash
        print(f"Error scraping Craigslist: {e}")
    
    return listings


def _parse_price(price_text: Optional[str]) -> Optional[float]:
    """
    Parse price from text like '$12,000' or '12000' to float
    
    Args:
        price_text: Raw price string
        
    Returns:
        Float price or None if unparseable
    """
    if not price_text:
        return None
    
    # Remove currency symbols, commas, and whitespace
    clean = price_text.replace('$', '').replace(',', '').strip()
    
    try:
        return float(clean)
    except (ValueError, AttributeError):
        return None


def _extract_listing_details(url: str) -> Dict[str, Optional[any]]:
    """
    Extract detailed information from a listing page, including odometer
    
    Args:
        url: Full URL to the listing page
        
    Returns:
        Dict with keys: year, make, model, mileage (in km)
        
    Note:
        This makes an additional HTTP request per listing, so use sparingly
    """
    details = {
        'year': None,
        'make': None,
        'model': None,
        'mileage': None
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract odometer from attributes section
        # Look for patterns like "odometer: 88000" or "odómetro: 88,000"
        attr_groups = soup.find_all('div', class_='attrgroup')
        
        for group in attr_groups:
            # Look for odometer span
            odometer_span = group.find('span', string=re.compile(r'od[oó]metro', re.IGNORECASE))
            if odometer_span:
                # Get the next sibling or text
                parent = odometer_span.parent
                if parent:
                    text = parent.get_text(strip=True)
                    # Extract number from text like "odómetro: 88000" or "odometer: 88,000"
                    match = re.search(r'(\d{1,3}(?:[,\s]\d{3})*)', text)
                    if match:
                        # Remove commas and spaces
                        mileage_str = match.group(1).replace(',', '').replace(' ', '')
                        try:
                            details['mileage'] = int(mileage_str)
                        except ValueError:
                            pass
            
            # Look for year, make, model in other attributes
            # Craigslist often shows "2016 renault koleos" in the attributes
            for span in group.find_all('span'):
                text = span.get_text(strip=True).lower()
                # Try to find year make model pattern
                year_match = re.search(r'\b(19[9]\d|20[0-2]\d)\b', text)
                if year_match and not details['year']:
                    details['year'] = int(year_match.group(1))
                
                # Check if this text contains a known make
                for make in ['renault', 'peugeot', 'seat', 'honda', 'toyota', 'ford', 'nissan', 
                             'chevrolet', 'gmc', 'dodge', 'jeep', 'volkswagen', 'bmw', 'mercedes',
                             'audi', 'mazda', 'hyundai', 'kia', 'suzuki', 'mitsubishi']:
                    if make in text and not details['make']:
                        details['make'] = make.title()
                        # Try to extract model (words after make)
                        model_match = re.search(rf'{make}\s+(\w+)', text)
                        if model_match:
                            details['model'] = model_match.group(1).title()
        
        # Small delay between requests
        time.sleep(0.5)
        
    except Exception as e:
        # Return partial details on error
        print(f"  [WARN] Error fetching details from {url}: {e}")
    
    return details


if __name__ == "__main__":
    # Manual testing
    print("Testing Craigslist scraper with detail fetching...")
    listings = scrape_craigslist_tijuana(max_results=5, fetch_details=True)
    print(f"\n{'='*80}")
    print(f"Found {len(listings)} listings\n")
    for i, listing in enumerate(listings, 1):
        print(f"{i}. {listing['title']}")
        print(f"   Price: ${listing.get('price', 'N/A')}")
        print(f"   Make: {listing.get('make', 'N/A')}, Model: {listing.get('model', 'N/A')}")
        print(f"   Year: {listing.get('year', 'N/A')}, Mileage: {listing.get('mileage', 'N/A')} km")
        print(f"   URL: {listing['url'][:60]}...")
        print()

