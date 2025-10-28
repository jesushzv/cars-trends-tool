"""
Mercado Libre Scraper for Tijuana/Baja California Car Listings
Phase 6: Add second data source
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


def scrape_mercadolibre_tijuana(max_results: int = 10, fetch_details: bool = False) -> List[Dict]:
    """
    Scrape car listings from Mercado Libre (Baja California region)
    Phase 10: Added engagement metrics (views)
    
    Args:
        max_results: Maximum number of listings to return
        fetch_details: If True, fetch detailed info from each listing page (slower but more accurate)
        
    Returns:
        List of dicts with keys: title, price, url, make, model, year, mileage, views
        Example: [
            {
                'title': '2016 Renault Koleos Privilege',
                'price': 180000.0,
                'url': 'https://www.mercadolibre.com.mx/...',
                'make': 'Renault',
                'model': 'Koleos',
                'year': 2016,
                'mileage': 88000,
                'views': 150  # Phase 10
            }
        ]
    """
    listings = []
    
    try:
        # Mercado Libre URL for cars in Baja California
        # Using _NoIndex_ to skip items without specific locations
        url = "https://autos.mercadolibre.com.mx/autos-camionetas/baja-california/"
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
        }
        
        # Make request
        print(f"Fetching Mercado Libre listings from: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all listing items
        # Mercado Libre typically uses <li class="ui-search-layout__item"> for each listing
        items = soup.find_all('li', class_='ui-search-layout__item')
        
        if not items:
            # Try alternative class names
            items = soup.find_all('div', class_='andes-card')
        
        if not items:
            print(f"[WARN] No listings found. HTML structure may have changed.")
            print(f"[DEBUG] First 500 chars of response: {response.text[:500]}")
        
        items = items[:max_results]
        print(f"Found {len(items)} listings on search page, processing...")
        
        for idx, item in enumerate(items, 1):
            try:
                # Extract title
                title_elem = item.find('h2', class_='ui-search-item__title')
                if not title_elem:
                    title_elem = item.find('h2')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                # Extract URL
                link_elem = item.find('a', class_='ui-search-link')
                if not link_elem:
                    link_elem = item.find('a', href=True)
                if not link_elem or not link_elem.get('href'):
                    continue
                listing_url = link_elem['href']
                
                # Make URL absolute if needed
                if not listing_url.startswith('http'):
                    listing_url = 'https://www.mercadolibre.com.mx' + listing_url
                
                # Extract price
                price_elem = item.find('span', class_='andes-money-amount__fraction')
                if not price_elem:
                    price_elem = item.find('span', class_='price-tag-fraction')
                price = None
                if price_elem:
                    price = _parse_price(price_elem.get_text(strip=True))
                
                # Parse title for car details
                car_info = parse_listing_title(title)
                
                # Initialize engagement metrics
                views = None
                
                # If fetch_details is True, get more accurate data from the listing page
                if fetch_details:
                    print(f"  [{idx}/{len(items)}] Fetching details for: {title[:50]}...")
                    detail_info = _extract_listing_details(listing_url)
                    
                    # Merge detail info with parsed info
                    if detail_info.get('make'):
                        car_info['make'] = detail_info['make']
                    if detail_info.get('model'):
                        car_info['model'] = detail_info['model']
                    if detail_info.get('year'):
                        car_info['year'] = detail_info['year']
                    if detail_info.get('mileage'):
                        car_info['mileage'] = detail_info['mileage']
                    # Extract engagement metrics (Phase 10)
                    if detail_info.get('views'):
                        views = detail_info['views']
                
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
                    'mileage': normalized.get('mileage'),
                    'views': views  # Phase 10: engagement metrics
                })
                
            except Exception as e:
                # Skip individual listing errors
                print(f"  [ERROR] Failed to process listing: {e}")
                continue
        
        # Add small delay to be respectful
        time.sleep(1)
        
    except Exception as e:
        # Return empty list on error, don't crash
        print(f"Error scraping Mercado Libre: {e}")
    
    return listings


def _parse_price(price_text: Optional[str]) -> Optional[float]:
    """
    Parse price from text like '180,000' or '180000' to float
    
    Args:
        price_text: Raw price string
        
    Returns:
        Float price or None if unparseable
    """
    if not price_text:
        return None
    
    # Remove currency symbols, commas, and whitespace
    clean = price_text.replace('$', '').replace(',', '').replace(' ', '').strip()
    
    try:
        return float(clean)
    except (ValueError, AttributeError):
        return None


def _extract_listing_details(url: str) -> Dict[str, Optional[any]]:
    """
    Extract detailed information from a listing page, including specs and engagement metrics
    Phase 10: Added engagement metrics extraction
    
    Args:
        url: Full URL to the listing page
        
    Returns:
        Dict with keys: year, make, model, mileage (in km), views
        
    Note:
        This makes an additional HTTP request per listing, so use sparingly
    """
    details = {
        'year': None,
        'make': None,
        'model': None,
        'mileage': None,
        'views': None
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept-Language': 'es-MX,es;q=0.9,en;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mercado Libre shows specifications in a table
        # Look for attributes like "Año", "Marca", "Modelo", "Kilómetros"
        spec_rows = soup.find_all('tr', class_='andes-table__row')
        
        for row in spec_rows:
            # Get the label and value
            label_elem = row.find('th')
            value_elem = row.find('td')
            
            if not label_elem or not value_elem:
                continue
            
            label = label_elem.get_text(strip=True).lower()
            value = value_elem.get_text(strip=True)
            
            # Extract year
            if 'año' in label or 'year' in label:
                year_match = re.search(r'\b(19[9]\d|20[0-2]\d)\b', value)
                if year_match:
                    details['year'] = int(year_match.group(1))
            
            # Extract make
            elif 'marca' in label or 'make' in label:
                details['make'] = value.title()
            
            # Extract model
            elif 'modelo' in label or 'model' in label:
                details['model'] = value.title()
            
            # Extract mileage (kilómetros)
            elif 'kilómetro' in label or 'km' in label:
                # Extract number from "88,000 km" or "88000"
                mileage_match = re.search(r'(\d{1,3}(?:[,\s]\d{3})*)', value)
                if mileage_match:
                    mileage_str = mileage_match.group(1).replace(',', '').replace(' ', '')
                    try:
                        details['mileage'] = int(mileage_str)
                    except ValueError:
                        pass
        
        # Extract views count (Phase 10)
        # Mercado Libre shows views as "X visitas" or similar
        views_elem = soup.find('span', string=re.compile(r'visita', re.IGNORECASE))
        if views_elem:
            views_text = views_elem.get_text()
            views_match = re.search(r'(\d{1,3}(?:[,\s]\d{3})*)', views_text)
            if views_match:
                views_str = views_match.group(1).replace(',', '').replace(' ', '')
                try:
                    details['views'] = int(views_str)
                except ValueError:
                    pass
        
        # Small delay between requests
        time.sleep(0.5)
        
    except Exception as e:
        # Return partial details on error
        print(f"  [WARN] Error fetching details from {url}: {e}")
    
    return details


if __name__ == "__main__":
    # Manual testing
    print("Testing Mercado Libre scraper...")
    listings = scrape_mercadolibre_tijuana(max_results=5, fetch_details=False)
    print(f"\n{'='*80}")
    print(f"Found {len(listings)} listings\n")
    for i, listing in enumerate(listings, 1):
        print(f"{i}. {listing['title']}")
        print(f"   Price: ${listing.get('price', 'N/A')}")
        print(f"   Make: {listing.get('make', 'N/A')}, Model: {listing.get('model', 'N/A')}")
        print(f"   Year: {listing.get('year', 'N/A')}, Mileage: {listing.get('mileage', 'N/A')} km")
        print(f"   URL: {listing['url'][:70]}...")
        print()

