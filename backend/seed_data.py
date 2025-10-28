"""
Initial Data Seeding Script
Phase 19.6: Pre-populate database with initial scraping

Runs initial scraping of all platforms if database is empty.
This ensures new deployments have immediate value for users.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import logging
from models import Listing
from database import SessionLocal, create_tables
from services.trends_service import create_daily_snapshot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def count_listings() -> int:
    """Count total listings in database"""
    db = SessionLocal()
    try:
        return db.query(Listing).count()
    finally:
        db.close()


def seed_initial_data() -> dict:
    """
    Run initial scraping to populate database
    
    Only runs if database is empty.
    Scrapes all three platforms and creates initial snapshot.
    
    Returns:
        Dict with seeding results
    """
    logger.info("=" * 70)
    logger.info("DATA SEEDING CHECK")
    logger.info("=" * 70)
    
    # Ensure tables exist
    logger.info("Ensuring database tables exist...")
    create_tables()
    
    # Check if database already has data
    listing_count = count_listings()
    logger.info(f"Current database size: {listing_count} listings")
    
    if listing_count > 0:
        logger.info("✅ Database already has data - skipping seed")
        logger.info("=" * 70)
        return {
            "seeded": False,
            "reason": "Database already has data",
            "existing_count": listing_count
        }
    
    logger.info("🌱 Database is empty - starting initial data seeding...")
    logger.info("=" * 70)
    
    results = {
        "seeded": True,
        "platforms": {},
        "total_scraped": 0,
        "snapshot_created": False,
        "errors": []
    }
    
    # Scrape Craigslist
    logger.info("\n📍 Scraping Craigslist Tijuana...")
    try:
        from scrapers.craigslist import scrape_craigslist_tijuana
        cl_count = scrape_craigslist_tijuana()
        results["platforms"]["craigslist"] = {
            "success": True,
            "count": cl_count
        }
        results["total_scraped"] += cl_count
        logger.info(f"✅ Craigslist: {cl_count} listings scraped")
    except Exception as e:
        error_msg = f"Craigslist scraping failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        results["platforms"]["craigslist"] = {
            "success": False,
            "error": str(e)
        }
        results["errors"].append(error_msg)
    
    # Scrape Mercado Libre
    logger.info("\n📍 Scraping Mercado Libre Tijuana...")
    try:
        from scrapers.mercadolibre import scrape_mercadolibre_tijuana
        ml_count = scrape_mercadolibre_tijuana()
        results["platforms"]["mercadolibre"] = {
            "success": True,
            "count": ml_count
        }
        results["total_scraped"] += ml_count
        logger.info(f"✅ Mercado Libre: {ml_count} listings scraped")
    except Exception as e:
        error_msg = f"Mercado Libre scraping failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        results["platforms"]["mercadolibre"] = {
            "success": False,
            "error": str(e)
        }
        results["errors"].append(error_msg)
    
    # Scrape Facebook (fail gracefully with alerting as per user request)
    logger.info("\n📍 Scraping Facebook Marketplace Tijuana...")
    try:
        from scrapers.facebook_marketplace import scrape_facebook_tijuana
        fb_count = scrape_facebook_tijuana()
        results["platforms"]["facebook"] = {
            "success": True,
            "count": fb_count
        }
        results["total_scraped"] += fb_count
        logger.info(f"✅ Facebook: {fb_count} listings scraped")
    except Exception as e:
        error_msg = f"Facebook Marketplace scraping failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error("⚠️  ALERT: Facebook scraping failed during initial seed!")
        logger.error("   This may be due to missing cookies or authentication.")
        logger.error("   See backend/HOW_TO_GET_FB_COOKIES.md for setup instructions.")
        logger.error("   Continuing with Craigslist and Mercado Libre data...")
        
        results["platforms"]["facebook"] = {
            "success": False,
            "error": str(e),
            "alert": "FACEBOOK_SCRAPING_FAILED"
        }
        results["errors"].append(error_msg)
    
    # Create initial daily snapshot
    if results["total_scraped"] > 0:
        logger.info("\n📊 Creating initial daily snapshot...")
        try:
            snapshot_result = create_daily_snapshot()
            results["snapshot_created"] = True
            results["snapshot"] = snapshot_result
            logger.info(f"✅ Snapshot created: {snapshot_result['snapshots_created']} cars tracked")
        except Exception as e:
            error_msg = f"Snapshot creation failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            results["errors"].append(error_msg)
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("SEEDING COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Total listings scraped: {results['total_scraped']}")
    logger.info(f"Successful platforms: {sum(1 for p in results['platforms'].values() if p['success'])}/3")
    
    if results["errors"]:
        logger.warning(f"⚠️  {len(results['errors'])} error(s) occurred:")
        for error in results["errors"]:
            logger.warning(f"   - {error}")
    
    if results["total_scraped"] > 0:
        logger.info("✅ Database seeded successfully!")
    else:
        logger.error("❌ No data was scraped - all platforms failed!")
    
    logger.info("=" * 70)
    
    return results


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    result = seed_initial_data()
    
    # Exit with appropriate status code
    if result["seeded"] and result["total_scraped"] > 0:
        sys.exit(0)  # Success
    elif not result["seeded"]:
        sys.exit(0)  # Skipped (already has data) - not an error
    else:
        sys.exit(1)  # Failed to scrape any data

