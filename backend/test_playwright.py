"""
Simple test to verify Playwright installation
"""
from playwright.sync_api import sync_playwright

print("Testing Playwright installation...")
print("=" * 60)

try:
    with sync_playwright() as p:
        print("✓ Playwright imported successfully")
        
        browser = p.chromium.launch(headless=True)
        print("✓ Chromium browser launched")
        
        page = browser.new_page()
        print("✓ New page created")
        
        page.goto('https://www.google.com', timeout=10000)
        print(f"✓ Navigated to page")
        print(f"  Page title: {page.title()}")
        
        browser.close()
        print("✓ Browser closed")
        
        print("\n" + "=" * 60)
        print("✅ Playwright is working correctly!")
        print("=" * 60)
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPlaywright may not be installed correctly.")

