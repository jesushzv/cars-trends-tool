"""
Analytics Service for car market insights
Phase 8: Basic Analytics - Top Cars
"""
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func
from database import SessionLocal
from models import Listing
from typing import List, Dict, Optional


def get_top_cars(limit: int = 20, platform: Optional[str] = None) -> List[Dict]:
    """
    Get the most frequently listed cars by make and model
    
    Args:
        limit: Maximum number of results to return (default: 20)
        platform: Optional platform filter ('craigslist', 'mercadolibre')
        
    Returns:
        List of dicts with keys: make, model, count, avg_price, min_price, max_price
        
    Example:
        [
            {
                'make': 'Honda',
                'model': 'CR-V',
                'count': 5,
                'avg_price': 25000.0,
                'min_price': 20000.0,
                'max_price': 30000.0
            },
            ...
        ]
    """
    db = SessionLocal()
    
    try:
        # Build query
        query = db.query(
            Listing.make,
            Listing.model,
            func.count(Listing.id).label('count'),
            func.avg(Listing.price).label('avg_price'),
            func.min(Listing.price).label('min_price'),
            func.max(Listing.price).label('max_price')
        )
        
        # Filter out null makes and models (incomplete data)
        query = query.filter(Listing.make.isnot(None), Listing.model.isnot(None))
        
        # Optional platform filter
        if platform:
            query = query.filter(Listing.platform == platform)
        
        # Group by make and model, order by count descending
        query = query.group_by(Listing.make, Listing.model)
        query = query.order_by(func.count(Listing.id).desc())
        query = query.limit(limit)
        
        results = query.all()
        
        # Format results
        top_cars = [
            {
                'make': row.make,
                'model': row.model,
                'count': row.count,
                'avg_price': round(row.avg_price, 2) if row.avg_price else None,
                'min_price': round(row.min_price, 2) if row.min_price else None,
                'max_price': round(row.max_price, 2) if row.max_price else None
            }
            for row in results
        ]
        
        return top_cars
        
    finally:
        db.close()


def get_top_makes(limit: int = 10, platform: Optional[str] = None) -> List[Dict]:
    """
    Get the most frequently listed car brands/makes
    
    Args:
        limit: Maximum number of results to return (default: 10)
        platform: Optional platform filter ('craigslist', 'mercadolibre')
        
    Returns:
        List of dicts with keys: make, count, models_count, avg_price
        
    Example:
        [
            {
                'make': 'Honda',
                'count': 15,
                'models_count': 5,
                'avg_price': 22000.0
            },
            ...
        ]
    """
    db = SessionLocal()
    
    try:
        # Build query
        query = db.query(
            Listing.make,
            func.count(Listing.id).label('count'),
            func.count(func.distinct(Listing.model)).label('models_count'),
            func.avg(Listing.price).label('avg_price')
        )
        
        # Filter out null makes
        query = query.filter(Listing.make.isnot(None))
        
        # Optional platform filter
        if platform:
            query = query.filter(Listing.platform == platform)
        
        # Group by make, order by count descending
        query = query.group_by(Listing.make)
        query = query.order_by(func.count(Listing.id).desc())
        query = query.limit(limit)
        
        results = query.all()
        
        # Format results
        top_makes = [
            {
                'make': row.make,
                'count': row.count,
                'models_count': row.models_count,
                'avg_price': round(row.avg_price, 2) if row.avg_price else None
            }
            for row in results
        ]
        
        return top_makes
        
    finally:
        db.close()


def get_market_summary(platform: Optional[str] = None) -> Dict:
    """
    Get overall market summary statistics
    
    Args:
        platform: Optional platform filter ('craigslist', 'mercadolibre')
        
    Returns:
        Dict with summary statistics
        
    Example:
        {
            'total_listings': 100,
            'unique_makes': 15,
            'unique_models': 45,
            'avg_price': 18500.0,
            'avg_year': 2018,
            'avg_mileage': 75000
        }
    """
    db = SessionLocal()
    
    try:
        # Build base query
        query = db.query(Listing)
        
        # Optional platform filter
        if platform:
            query = query.filter(Listing.platform == platform)
        
        # Get summary statistics
        total_listings = query.count()
        
        # Count unique makes (SQLite-compatible way)
        unique_makes_query = db.query(Listing.make)\
            .filter(Listing.make.isnot(None))
        if platform:
            unique_makes_query = unique_makes_query.filter(Listing.platform == platform)
        unique_makes = unique_makes_query.distinct().count()
        
        # Count unique models (SQLite-compatible way)
        unique_models_query = db.query(Listing.model)\
            .filter(Listing.model.isnot(None))
        if platform:
            unique_models_query = unique_models_query.filter(Listing.platform == platform)
        unique_models = unique_models_query.distinct().count()
        
        # Get averages (only for non-null values)
        avg_price = db.query(func.avg(Listing.price))\
            .filter(Listing.price.isnot(None))
        if platform:
            avg_price = avg_price.filter(Listing.platform == platform)
        avg_price = avg_price.scalar()
        
        avg_year = db.query(func.avg(Listing.year))\
            .filter(Listing.year.isnot(None))
        if platform:
            avg_year = avg_year.filter(Listing.platform == platform)
        avg_year = avg_year.scalar()
        
        avg_mileage = db.query(func.avg(Listing.mileage))\
            .filter(Listing.mileage.isnot(None))
        if platform:
            avg_mileage = avg_mileage.filter(Listing.platform == platform)
        avg_mileage = avg_mileage.scalar()
        
        return {
            'total_listings': total_listings,
            'unique_makes': unique_makes,
            'unique_models': unique_models,
            'avg_price': round(avg_price, 2) if avg_price else None,
            'avg_year': int(avg_year) if avg_year else None,
            'avg_mileage': int(avg_mileage) if avg_mileage else None
        }
        
    finally:
        db.close()


def get_price_distribution(platform: Optional[str] = None) -> Dict:
    """
    Get price distribution statistics
    
    Args:
        platform: Optional platform filter ('craigslist', 'mercadolibre')
        
    Returns:
        Dict with price ranges and their listing counts
        
    Example:
        {
            'ranges': [
                {'range': '0-100k', 'min': 0, 'max': 100000, 'count': 5},
                {'range': '100k-200k', 'min': 100000, 'max': 200000, 'count': 3},
                ...
            ],
            'total_with_price': 15,
            'total_without_price': 5
        }
    """
    db = SessionLocal()
    
    try:
        # Build base query
        query = db.query(Listing)
        
        # Optional platform filter
        if platform:
            query = query.filter(Listing.platform == platform)
        
        # Count listings with and without prices
        total_with_price = query.filter(Listing.price.isnot(None)).count()
        total_without_price = query.filter(Listing.price.is_(None)).count()
        
        # Define price ranges (in thousands)
        ranges = [
            {'range': '0-100k', 'min': 0, 'max': 100000},
            {'range': '100k-200k', 'min': 100000, 'max': 200000},
            {'range': '200k-300k', 'min': 200000, 'max': 300000},
            {'range': '300k-500k', 'min': 300000, 'max': 500000},
            {'range': '500k-700k', 'min': 500000, 'max': 700000},
            {'range': '700k-1M', 'min': 700000, 'max': 1000000},
            {'range': '1M+', 'min': 1000000, 'max': None},
        ]
        
        # Count listings in each range
        for price_range in ranges:
            range_query = query.filter(Listing.price >= price_range['min'])
            if price_range['max']:
                range_query = range_query.filter(Listing.price < price_range['max'])
            price_range['count'] = range_query.count()
        
        return {
            'ranges': ranges,
            'total_with_price': total_with_price,
            'total_without_price': total_without_price
        }
        
    finally:
        db.close()


def get_price_by_year(platform: Optional[str] = None) -> List[Dict]:
    """
    Get average price by vehicle year
    
    Args:
        platform: Optional platform filter ('craigslist', 'mercadolibre')
        
    Returns:
        List of dicts with year and avg price
        
    Example:
        [
            {'year': 2023, 'avg_price': 650000.0, 'count': 5},
            {'year': 2022, 'avg_price': 550000.0, 'count': 3},
            ...
        ]
    """
    db = SessionLocal()
    
    try:
        # Build query
        query = db.query(
            Listing.year,
            func.avg(Listing.price).label('avg_price'),
            func.count(Listing.id).label('count')
        )
        
        # Filter out null years and prices
        query = query.filter(Listing.year.isnot(None), Listing.price.isnot(None))
        
        # Optional platform filter
        if platform:
            query = query.filter(Listing.platform == platform)
        
        # Group by year, order by year descending
        query = query.group_by(Listing.year)
        query = query.order_by(Listing.year.desc())
        
        results = query.all()
        
        # Format results
        price_by_year = [
            {
                'year': row.year,
                'avg_price': round(row.avg_price, 2) if row.avg_price else None,
                'count': row.count
            }
            for row in results
        ]
        
        return price_by_year
        
    finally:
        db.close()


def compare_platforms() -> Dict:
    """
    Compare pricing between Craigslist and Mercado Libre
    
    Returns:
        Dict with comparison statistics
        
    Example:
        {
            'craigslist': {'avg_price': 150000.0, 'count': 10, 'avg_year': 2018},
            'mercadolibre': {'avg_price': 550000.0, 'count': 13, 'avg_year': 2022},
            'difference': 400000.0,
            'difference_pct': 266.67
        }
    """
    db = SessionLocal()
    
    try:
        # Get stats for each platform
        platforms_data = {}
        
        for platform in ['craigslist', 'mercadolibre']:
            query = db.query(Listing).filter(Listing.platform == platform)
            
            count = query.count()
            
            avg_price = db.query(func.avg(Listing.price))\
                .filter(Listing.platform == platform, Listing.price.isnot(None))\
                .scalar()
            
            avg_year = db.query(func.avg(Listing.year))\
                .filter(Listing.platform == platform, Listing.year.isnot(None))\
                .scalar()
            
            platforms_data[platform] = {
                'avg_price': round(avg_price, 2) if avg_price else None,
                'count': count,
                'avg_year': int(avg_year) if avg_year else None
            }
        
        # Calculate difference
        diff = None
        diff_pct = None
        if (platforms_data['craigslist']['avg_price'] and 
            platforms_data['mercadolibre']['avg_price']):
            diff = platforms_data['mercadolibre']['avg_price'] - platforms_data['craigslist']['avg_price']
            diff_pct = (diff / platforms_data['craigslist']['avg_price']) * 100
        
        return {
            'craigslist': platforms_data['craigslist'],
            'mercadolibre': platforms_data['mercadolibre'],
            'difference': round(diff, 2) if diff else None,
            'difference_pct': round(diff_pct, 2) if diff_pct else None
        }
        
    finally:
        db.close()


if __name__ == "__main__":
    # Test the analytics service
    print("Testing Analytics Service...")
    print("="*80)
    
    print("\n1. Top Cars:")
    top_cars = get_top_cars(limit=10)
    for i, car in enumerate(top_cars, 1):
        print(f"  {i}. {car['make']} {car['model']}: {car['count']} listings")
        if car['avg_price']:
            print(f"      Price: ${car['avg_price']:,.0f} (${car['min_price']:,.0f} - ${car['max_price']:,.0f})")
    
    print("\n2. Top Makes:")
    top_makes = get_top_makes(limit=5)
    for i, make in enumerate(top_makes, 1):
        print(f"  {i}. {make['make']}: {make['count']} listings ({make['models_count']} models)")
        if make['avg_price']:
            print(f"      Avg Price: ${make['avg_price']:,.0f}")
    
    print("\n3. Market Summary:")
    summary = get_market_summary()
    print(f"  Total Listings: {summary['total_listings']}")
    print(f"  Unique Makes: {summary['unique_makes']}")
    print(f"  Unique Models: {summary['unique_models']}")
    if summary['avg_price']:
        print(f"  Average Price: ${summary['avg_price']:,.0f}")
    if summary['avg_year']:
        print(f"  Average Year: {summary['avg_year']}")
    if summary['avg_mileage']:
        print(f"  Average Mileage: {summary['avg_mileage']:,} km")
    
    print("\n4. Price Distribution:")
    dist = get_price_distribution()
    for r in dist['ranges']:
        if r['count'] > 0:
            print(f"  {r['range']}: {r['count']} listings")
    
    print("\n5. Platform Comparison:")
    comparison = compare_platforms()
    if comparison['craigslist']['avg_price'] and comparison['mercadolibre']['avg_price']:
        print(f"  Craigslist: {comparison['craigslist']['count']} listings, avg ${comparison['craigslist']['avg_price']:,.0f}")
        print(f"  Mercado Libre: {comparison['mercadolibre']['count']} listings, avg ${comparison['mercadolibre']['avg_price']:,.0f}")
        if comparison['difference']:
            print(f"  Difference: ${comparison['difference']:,.0f} ({comparison['difference_pct']:.1f}%)")
    else:
        print(f"  No data available for comparison")

