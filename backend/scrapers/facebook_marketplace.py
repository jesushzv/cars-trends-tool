"""
Facebook Marketplace Scraper for Tijuana Car Listings
Phase 11: Third data source with engagement metrics

NOTE: This scraper requires authentication (cookies) to work properly.
See FB_MARKETPLACE_RESEARCH.md for details.

SETUP REQUIRED (choose one):
1. Preferred (Production): set env var FACEBOOK_COOKIES_JSON to a JSON object of cookies
2. Local dev: export cookies and save to backend/fb_cookies.json
3. Run the scraper

The scraper uses Playwright for JavaScript rendering.
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import time
import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.parser import parse_listing_title
from utils.normalizer import normalize_car_data


def scrape_facebook_tijuana(max_results: int = 10, headless: bool = True) -> List[Dict]:
    """
    Scrape car listings from Facebook Marketplace (Tijuana region) using Playwright
    
    REQUIRES: fb_cookies.json file with Facebook authentication cookies
    See fb_cookies.json.template for setup instructions
    
    Args:
        max_results: Maximum number of listings to return (default: 10)
        headless: Run browser in headless mode (default: True)
        
    Returns:
        List of dicts with keys: title, price, url, make, model, year, mileage, 
                                 views, likes, comments (engagement metrics)
        Example: [
            {
                'title': '2020 Honda Civic EX',
                'price': 18000.0,
                'url': 'https://www.facebook.com/marketplace/item/123456',
                'make': 'Honda',
                'model': 'Civic',
                'year': 2020,
                'mileage': 45000,
                'views': None,  # May not be available
                'likes': 25,
                'comments': 5
            }
        ]
    """
    listings = []
    
    print("[INFO] Facebook Marketplace scraper (Playwright)")
    print("[INFO] Checking for authentication cookies...")
    
    # Load cookies
    cookies = _load_cookies()
    if not cookies:
        print("[ERROR] No Facebook cookies found!")
        print("[INFO] To use Facebook Marketplace scraper:")
        print("  1. Copy backend/fb_cookies.json.template to backend/fb_cookies.json")
        print("  2. Log into Facebook in your browser")
        print("  3. Export cookies and paste into fb_cookies.json")
        print("  4. See FB_MARKETPLACE_RESEARCH.md for details")
        return listings
    
    print(f"[INFO] Loaded {len(cookies)} cookies")
    
    try:
        with sync_playwright() as p:
            # Launch browser
            print(f"[INFO] Launching browser (headless={headless})...")
            browser = p.chromium.launch(headless=headless)
            
            # Create context with cookies
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='es-MX'
            )
            
            # Add cookies to context
            # Convert cookie format if needed
            playwright_cookies = _convert_cookies_to_playwright(cookies)
            if playwright_cookies:
                context.add_cookies(playwright_cookies)
                print(f"[INFO] Added {len(playwright_cookies)} cookies to browser context")
            
            page = context.new_page()
            
            # Navigate to Facebook Marketplace - Tijuana vehicles
            # Using the general vehicles category URL
            marketplace_url = "https://www.facebook.com/marketplace/category/vehicles"
            print(f"[INFO] Navigating to: {marketplace_url}")
            
            try:
                page.goto(marketplace_url, wait_until='domcontentloaded', timeout=30000)
                print("[INFO] Page loaded")
                
                # Wait a bit for JavaScript to render
                time.sleep(3)
                
                # Check if we're logged in
                page_content = page.content()
                if 'login' in page.url.lower() or 'login' in page_content.lower()[:1000]:
                    print("[ERROR] Not logged in - cookies may be invalid or expired")
                    print("[INFO] Please export fresh cookies from Facebook")
                    browser.close()
                    return listings
                
                print("[SUCCESS] Authenticated successfully!")
                
                # Extract listings
                print(f"[INFO] Extracting up to {max_results} listings...")
                listings = _extract_listings_from_page(page, max_results)
                
                print(f"[INFO] Found {len(listings)} listings")
                
                # Take screenshot for debugging (if not headless)
                if not headless:
                    screenshot_path = os.path.join(os.path.dirname(__file__), '..', 'fb_marketplace_debug.png')
                    page.screenshot(path=screenshot_path)
                    print(f"[DEBUG] Screenshot saved to: {screenshot_path}")
                
            except PlaywrightTimeout:
                print("[ERROR] Page load timeout - Facebook may be slow or blocking")
            except Exception as e:
                print(f"[ERROR] Navigation error: {e}")
            
            finally:
                browser.close()
                print("[INFO] Browser closed")
        
    except Exception as e:
        print(f"[ERROR] Playwright error: {e}")
        import traceback
        traceback.print_exc()
    
    return listings


def _extract_listings_from_page(page, max_results: int) -> List[Dict]:
    """
    Extract car listings from Facebook Marketplace page
    
    NOTE: Facebook's HTML structure changes frequently. This function uses
    multiple fallback strategies to find listings.
    
    Args:
        page: Playwright page object
        max_results: Maximum number of listings to extract
        
    Returns:
        List of listing dicts
    """
    listings = []
    
    try:
        # Wait for content to load
        print("[DEBUG] Waiting for marketplace content to load...")
        time.sleep(2)
        
        # Get page content
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Strategy 1: Look for marketplace item links
        # Facebook uses URLs like: /marketplace/item/123456789
        listing_links = soup.find_all('a', href=re.compile(r'/marketplace/item/\d+'))
        
        if not listing_links:
            # Strategy 2: Look for any links with "marketplace" in them
            listing_links = soup.find_all('a', href=re.compile(r'marketplace'))
            print(f"[DEBUG] Strategy 2: Found {len(listing_links)} marketplace links")
        
        if not listing_links:
            print("[WARN] No listing links found on page")
            print("[DEBUG] This could mean:")
            print("  - Facebook's structure has changed")
            print("  - Page didn't load completely")
            print("  - Wrong region/category")
            return listings
        
        print(f"[DEBUG] Found {len(listing_links)} potential listing links")
        
        # Process unique listings
        seen_urls = set()
        
        for link in listing_links[:max_results * 3]:  # Get more than needed for filtering
            try:
                href = link.get('href', '')
                
                # Extract item ID from URL
                item_match = re.search(r'/marketplace/item/(\d+)', href)
                if not item_match:
                    continue
                
                item_id = item_match.group(1)
                listing_url = f"https://www.facebook.com/marketplace/item/{item_id}"
                
                # Skip duplicates
                if listing_url in seen_urls:
                    continue
                seen_urls.add(listing_url)
                
                # Extract basic info from the search results page
                listing_data = {
                    'url': listing_url,
                    'title': None,
                    'price': None,
                    'make': None,
                    'model': None,
                    'year': None,
                    'mileage': None,
                    'views': None,
                    'likes': None,
                    'comments': None
                }
                
                # Try to extract title and price from the link's container
                parent = link.find_parent('div', recursive=True)
                if parent:
                    # Title (usually in the link text or nearby span)
                    title_text = link.get_text(strip=True)
                    if title_text and len(title_text) > 3:
                        listing_data['title'] = title_text
                    
                    # Price (look for $ signs in nearby text)
                    price_elements = parent.find_all(string=re.compile(r'\$[\d,]+'))
                    if price_elements:
                        price_text = price_elements[0]
                        listing_data['price'] = _parse_price(price_text)
                
                # Parse car details from title
                if listing_data['title']:
                    parsed = parse_listing_title(listing_data['title'])
                    if parsed:
                        listing_data['make'] = parsed.get('make')
                        listing_data['model'] = parsed.get('model')
                        listing_data['year'] = parsed.get('year')
                        listing_data['mileage'] = parsed.get('mileage')
                
                # Add all valid URLs (we'll fetch details later if needed)
                listings.append(listing_data)
                print(f"  [{len(listings)}] {listing_data['title'][:50] if listing_data['title'] else '(will fetch details)'} - ${listing_data['price'] if listing_data['price'] else 'TBD'}")
                
                # Stop if we have enough
                if len(listings) >= max_results:
                    break
                    
            except Exception as e:
                print(f"[WARN] Error processing listing link: {e}")
                continue
        
        # Fetch details for listings that don't have complete data
        print(f"[INFO] Fetching detailed information for {len(listings)} listings...")
        for i, listing in enumerate(listings[:max_results], 1):
            if not listing['title'] or not listing['price']:
                print(f"[INFO] [{i}/{len(listings)}] Fetching details for listing...")
                # Save HTML for first 3 listings for debugging engagement metrics
                save_html_debug = (i <= 3)
                _fetch_listing_details(page, listing, save_html=save_html_debug)
                time.sleep(3)  # Rate limiting - 3 seconds between requests
        
        return listings[:max_results]
        
    except Exception as e:
        print(f"[ERROR] Failed to extract listings: {e}")
        import traceback
        traceback.print_exc()
        return listings


def _fetch_listing_details(page, listing: Dict, save_html: bool = False) -> None:
    """
    Fetch detailed information for a single listing by visiting its page
    
    This function modifies the listing dict in place.
    
    Args:
        page: Playwright page object
        listing: Listing dict to enhance with details
        save_html: If True, save HTML to file for debugging
    """
    try:
        # Navigate to listing page
        page.goto(listing['url'], wait_until='domcontentloaded', timeout=15000)
        time.sleep(2)
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Save HTML for debugging if requested
        if save_html:
            item_id = listing['url'].split('/')[-1]
            debug_file = os.path.join(os.path.dirname(__file__), '..', f'fb_debug_listing_{item_id}.html')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"[DEBUG] Saved HTML to: {debug_file}")
        
        # Extract title (usually in h1 or large heading)
        if not listing['title']:
            title_elem = soup.find('h1') or soup.find('span', {'class': re.compile(r'.*title.*', re.I)})
            if title_elem:
                listing['title'] = title_elem.get_text(strip=True)
        
        # Extract price (look for $ with numbers)
        if not listing['price']:
            price_elems = soup.find_all(string=re.compile(r'\$[\d,]+'))
            if price_elems:
                listing['price'] = _parse_price(price_elems[0])
        
        # Extract description (might contain car details)
        description_elem = soup.find('div', {'data-testid': re.compile(r'.*description.*', re.I)})
        if description_elem:
            description = description_elem.get_text()
            
            # Look for mileage in description
            mileage_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(?:km|kilometers|miles|mi)', description, re.I)
            if mileage_match and not listing['mileage']:
                mileage_str = mileage_match.group(1).replace(',', '')
                try:
                    mileage_val = int(mileage_str)
                    # Convert miles to km if needed
                    if 'mi' in mileage_match.group(0).lower():
                        mileage_val = int(mileage_val * 1.60934)
                    listing['mileage'] = mileage_val
                except ValueError:
                    pass
        
        # Try to extract engagement metrics
        _extract_engagement_metrics(soup, listing)
        
        # Parse car details from title
        if listing['title'] and not listing['make']:
            parsed = parse_listing_title(listing['title'])
            if parsed:
                listing['make'] = parsed.get('make')
                listing['model'] = parsed.get('model')
                listing['year'] = parsed.get('year')
                if not listing['mileage']:
                    listing['mileage'] = parsed.get('mileage')
        
    except Exception as e:
        print(f"[WARN] Failed to fetch details for {listing['url']}: {e}")


def _extract_engagement_metrics(soup: BeautifulSoup, listing: Dict) -> None:
    """
    Attempt to extract engagement metrics from listing page
    
    IMPORTANT LIMITATION (Verified 2025-10-26):
    Facebook Marketplace does NOT publicly display engagement metrics (saves, views, interested count)
    on listing pages. These metrics are only visible to:
    - The seller in their seller dashboard
    - Facebook's internal systems
    
    This is by design - Facebook keeps engagement data private to prevent it from affecting
    negotiations between buyers and sellers.
    
    Result: This function will NOT find engagement data and will leave fields as None.
    The database schema supports these fields for future use with other platforms
    (Craigslist, Mercado Libre) that may expose engagement data.
    
    Args:
        soup: BeautifulSoup object of the listing page
        listing: Listing dict to update with metrics (will remain None for Facebook)
    """
    # Facebook Marketplace does not publicly expose engagement metrics
    # Keeping this function for consistency with the scraper architecture
    # and in case Facebook changes this policy in the future
    
    # The fields (views, likes, comments) will remain None for Facebook listings
    # This is expected and documented behavior
    pass


def _load_cookies() -> Optional[Dict]:
    """
    Load Facebook cookies from environment variable or JSON file.
    
    Order of precedence:
    1) FACEBOOK_COOKIES_JSON env var (JSON object)
    2) backend/fb_cookies.json file (local development)
    
    Returns:
        Dict of cookies or None if neither source is available/valid
    """
    # 1) Environment variable (preferred for production)
    env_val = os.getenv("FACEBOOK_COOKIES_JSON")
    if env_val:
        try:
            cookies = json.loads(env_val)
            if isinstance(cookies, dict) and cookies:
                return cookies
            else:
                print("[WARN] FACEBOOK_COOKIES_JSON is set but is empty or not a JSON object")
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in FACEBOOK_COOKIES_JSON: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to parse FACEBOOK_COOKIES_JSON: {e}")
    
    # 2) Fallback to local file for development
    cookie_file = os.path.join(os.path.dirname(__file__), '..', 'fb_cookies.json')
    if not os.path.exists(cookie_file):
        return None
    try:
        with open(cookie_file, 'r') as f:
            cookies = json.load(f)
        # Check if it's the template file (has _comment key)
        if '_comment' in cookies or '_instructions' in cookies:
            print("[WARN] fb_cookies.json appears to be the template file")
            print("[WARN] Please replace with actual Facebook cookies")
            return None
        return cookies
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in fb_cookies.json: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to load cookies: {e}")
        return None


def _convert_cookies_to_playwright(cookies: Dict) -> List[Dict]:
    """
    Convert cookies from JSON export format to Playwright format
    
    Playwright expects cookies in this format:
    [
        {
            "name": "cookie_name",
            "value": "cookie_value",
            "domain": ".facebook.com",
            "path": "/",
            "httpOnly": True,
            "secure": True,
            "sameSite": "None"
        }
    ]
    
    Args:
        cookies: Dict of cookie_name: cookie_value pairs
        
    Returns:
        List of cookie dicts in Playwright format
    """
    playwright_cookies = []
    
    for name, value in cookies.items():
        # Skip non-cookie fields (like _comment, _instructions, etc)
        if name.startswith('_'):
            continue
        
        # Convert to Playwright format
        cookie = {
            'name': name,
            'value': str(value),
            'domain': '.facebook.com',
            'path': '/',
            'httpOnly': True,
            'secure': True,
            'sameSite': 'None'
        }
        playwright_cookies.append(cookie)
    
    return playwright_cookies


def _parse_price(price_text: Optional[str]) -> Optional[float]:
    """
    Parse price from Facebook Marketplace format
    Handles both US and Mexican/Spanish number formats:
    - US format: "$18,000" or "$18,000.50" (comma as thousands separator, period for cents)
    - Mexican format: "$40.000" (period as thousands separator, typically no cents)
    
    Strategy: Remove all commas and periods EXCEPT the last period if followed by 1-2 digits (cents)
    
    Args:
        price_text: Raw price string
        
    Returns:
        Float price or None if unparseable
    """
    if not price_text:
        return None
    
    # Remove currency symbols and whitespace
    clean = price_text.replace('$', '').replace('MX', '').replace(' ', '').strip()
    
    # Check if there's a decimal point (period followed by 1-2 digits at the end)
    # Examples: "15,000.50" or "15000.5"
    import re
    decimal_match = re.search(r'\.(\d{1,2})$', clean)
    
    if decimal_match:
        # Has cents - preserve the last period, remove all other commas and periods
        # Split on last period
        parts = clean.rsplit('.', 1)
        # Remove thousands separators from integer part
        integer_part = parts[0].replace(',', '').replace('.', '')
        # Reconstruct with decimal
        clean = f"{integer_part}.{parts[1]}"
    else:
        # No cents - remove all commas and periods (they're all thousands separators)
        # Mexican format: "40.000" -> "40000"
        # US format: "40,000" -> "40000"
        clean = clean.replace(',', '').replace('.', '')
    
    try:
        return float(clean)
    except (ValueError, AttributeError):
        return None


if __name__ == "__main__":
    # Manual testing
    print("=" * 80)
    print("Testing Facebook Marketplace scraper (Playwright)")
    print("=" * 80)
    
    # Test with headless mode (set to False to see browser)
    listings = scrape_facebook_tijuana(max_results=5, headless=False)
    
    print(f"\n{'='*80}")
    print(f"Result: Found {len(listings)} listings")
    print(f"{'='*80}")
    
    if len(listings) == 0:
        print("\n⚠️  No listings found")
        print("\nThis is expected if:")
        print("  • fb_cookies.json doesn't exist or is invalid")
        print("  • Cookies have expired")
        print("  • Facebook is blocking the scraper")
        print("\nSetup:")
        print("  1. Log into Facebook in your browser")
        print("  2. Export cookies using browser extension")
        print("  3. Copy backend/fb_cookies.json.template → backend/fb_cookies.json")
        print("  4. Paste your cookies into fb_cookies.json")
        print("  5. Run this script again")
    else:
        print("\n✅ Success! Found listings:")
        for i, listing in enumerate(listings, 1):
            print(f"\n{i}. {listing['title']}")
            print(f"   Price: ${listing.get('price', 'N/A')}")
            print(f"   Make: {listing.get('make', 'N/A')}, Model: {listing.get('model', 'N/A')}")
            print(f"   Year: {listing.get('year', 'N/A')}, Mileage: {listing.get('mileage', 'N/A')} km")
            print(f"   Engagement: Likes: {listing.get('likes', 'N/A')}, Views: {listing.get('views', 'N/A')}")
            print(f"   URL: {listing['url'][:70]}...")

