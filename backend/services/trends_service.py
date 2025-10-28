"""
Trends Service for tracking price changes over time
Phase 13: Time Series - Price Trends
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import func, case
from datetime import date, datetime, timedelta
from database import SessionLocal
from models import Listing, DailySnapshot
from typing import List, Dict, Optional


def create_daily_snapshot(snapshot_date: Optional[date] = None) -> Dict:
    """
    Create daily snapshots for all make/model combinations
    
    Args:
        snapshot_date: Date to create snapshot for (default: today)
        
    Returns:
        Dict with summary of snapshots created
        
    Example:
        result = create_daily_snapshot()
        # {
        #     'date': '2025-10-26',
        #     'snapshots_created': 15,
        #     'snapshots_updated': 3,
        #     'total_cars': 18
        # }
    """
    if snapshot_date is None:
        snapshot_date = date.today()
    
    db = SessionLocal()
    
    try:
        # Get all unique make/model combinations with stats
        results = db.query(
            Listing.make,
            Listing.model,
            func.count(Listing.id).label('count'),
            func.avg(Listing.price).label('avg_price'),
            func.min(Listing.price).label('min_price'),
            func.max(Listing.price).label('max_price'),
            func.sum(case((Listing.platform == 'craigslist', 1), else_=0)).label('craigslist_count'),
            func.sum(case((Listing.platform == 'mercadolibre', 1), else_=0)).label('mercadolibre_count'),
            func.sum(case((Listing.platform == 'facebook', 1), else_=0)).label('facebook_count')
        ).filter(
            Listing.make.isnot(None),
            Listing.model.isnot(None)
        ).group_by(
            Listing.make,
            Listing.model
        ).all()
        
        created_count = 0
        updated_count = 0
        
        for row in results:
            # Check if snapshot already exists for this date/make/model
            existing = db.query(DailySnapshot).filter(
                DailySnapshot.date == snapshot_date,
                DailySnapshot.make == row.make,
                DailySnapshot.model == row.model
            ).first()
            
            if existing:
                # Update existing snapshot
                existing.listing_count = row.count
                existing.avg_price = float(row.avg_price) if row.avg_price else None
                existing.min_price = float(row.min_price) if row.min_price else None
                existing.max_price = float(row.max_price) if row.max_price else None
                existing.craigslist_count = row.craigslist_count or 0
                existing.mercadolibre_count = row.mercadolibre_count or 0
                existing.facebook_count = row.facebook_count or 0
                updated_count += 1
            else:
                # Create new snapshot
                snapshot = DailySnapshot(
                    date=snapshot_date,
                    make=row.make,
                    model=row.model,
                    listing_count=row.count,
                    avg_price=float(row.avg_price) if row.avg_price else None,
                    min_price=float(row.min_price) if row.min_price else None,
                    max_price=float(row.max_price) if row.max_price else None,
                    craigslist_count=row.craigslist_count or 0,
                    mercadolibre_count=row.mercadolibre_count or 0,
                    facebook_count=row.facebook_count or 0
                )
                db.add(snapshot)
                created_count += 1
        
        db.commit()
        
        return {
            'date': snapshot_date.isoformat(),
            'snapshots_created': created_count,
            'snapshots_updated': updated_count,
            'total_cars': len(results)
        }
        
    finally:
        db.close()


def get_price_trend(make: str, model: str, days: int = 30) -> List[Dict]:
    """
    Get price trend for a specific make/model over time
    
    Args:
        make: Car make (e.g., 'Honda')
        model: Car model (e.g., 'Civic')
        days: Number of days to look back (default: 30)
        
    Returns:
        List of daily snapshots sorted by date (oldest first)
        
    Example:
        trend = get_price_trend('Honda', 'Civic', days=7)
        # [
        #     {
        #         'date': '2025-10-20',
        #         'avg_price': 18000.0,
        #         'listing_count': 12,
        #         'min_price': 15000.0,
        #         'max_price': 22000.0
        #     },
        #     ...
        # ]
    """
    db = SessionLocal()
    
    try:
        start_date = date.today() - timedelta(days=days)
        
        snapshots = db.query(DailySnapshot).filter(
            DailySnapshot.make == make,
            DailySnapshot.model == model,
            DailySnapshot.date >= start_date
        ).order_by(DailySnapshot.date.asc()).all()
        
        return [
            {
                'date': snap.date.isoformat(),
                'avg_price': snap.avg_price,
                'listing_count': snap.listing_count,
                'min_price': snap.min_price,
                'max_price': snap.max_price,
                'craigslist_count': snap.craigslist_count,
                'mercadolibre_count': snap.mercadolibre_count,
                'facebook_count': snap.facebook_count
            }
            for snap in snapshots
        ]
        
    finally:
        db.close()


def get_trending_cars(days: int = 7, limit: int = 10) -> List[Dict]:
    """
    Get cars with biggest price changes (trending up or down)
    
    Args:
        days: Number of days to compare (default: 7)
        limit: Maximum number of results (default: 10)
        
    Returns:
        List of cars with price change info, sorted by absolute change
        
    Example:
        trending = get_trending_cars(days=7, limit=5)
        # [
        #     {
        #         'make': 'Honda',
        #         'model': 'Civic',
        #         'old_price': 18000.0,
        #         'new_price': 19500.0,
        #         'change': 1500.0,
        #         'change_pct': 8.33,
        #         'direction': 'up'
        #     },
        #     ...
        # ]
    """
    db = SessionLocal()
    
    try:
        today = date.today()
        comparison_date = today - timedelta(days=days)
        
        # Get today's snapshots
        today_snapshots = db.query(DailySnapshot).filter(
            DailySnapshot.date == today,
            DailySnapshot.avg_price.isnot(None)
        ).all()
        
        trending = []
        
        for today_snap in today_snapshots:
            # Find comparison snapshot
            old_snap = db.query(DailySnapshot).filter(
                DailySnapshot.make == today_snap.make,
                DailySnapshot.model == today_snap.model,
                DailySnapshot.date == comparison_date,
                DailySnapshot.avg_price.isnot(None)
            ).first()
            
            if old_snap and old_snap.avg_price and today_snap.avg_price:
                change = today_snap.avg_price - old_snap.avg_price
                change_pct = (change / old_snap.avg_price) * 100
                
                trending.append({
                    'make': today_snap.make,
                    'model': today_snap.model,
                    'old_price': old_snap.avg_price,
                    'new_price': today_snap.avg_price,
                    'change': round(change, 2),
                    'change_pct': round(change_pct, 2),
                    'direction': 'up' if change > 0 else 'down',
                    'listing_count': today_snap.listing_count
                })
        
        # Sort by absolute change (biggest changes first)
        trending.sort(key=lambda x: abs(x['change']), reverse=True)
        
        return trending[:limit]
        
    finally:
        db.close()


def get_market_overview(days: int = 30) -> Dict:
    """
    Get overview of market trends
    
    Args:
        days: Number of days to analyze (default: 30)
        
    Returns:
        Dict with market statistics and trends
        
    Example:
        overview = get_market_overview(days=30)
        # {
        #     'total_unique_cars': 45,
        #     'avg_market_price': 22500.0,
        #     'total_snapshots': 450,
        #     'date_range': {
        #         'start': '2025-09-26',
        #         'end': '2025-10-26'
        #     },
        #     'most_listed': [
        #         {'make': 'Honda', 'model': 'Civic', 'avg_listings': 15},
        #         ...
        #     ]
        # }
    """
    db = SessionLocal()
    
    try:
        start_date = date.today() - timedelta(days=days)
        end_date = date.today()
        
        # Get all snapshots in range
        snapshots = db.query(DailySnapshot).filter(
            DailySnapshot.date >= start_date,
            DailySnapshot.date <= end_date
        ).all()
        
        if not snapshots:
            return {
                'total_unique_cars': 0,
                'avg_market_price': None,
                'total_snapshots': 0,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'most_listed': []
            }
        
        # Calculate stats
        unique_cars = set((snap.make, snap.model) for snap in snapshots)
        prices = [snap.avg_price for snap in snapshots if snap.avg_price]
        avg_price = sum(prices) / len(prices) if prices else None
        
        # Get most listed cars (by average daily count)
        car_listings = {}
        car_days = {}
        
        for snap in snapshots:
            key = (snap.make, snap.model)
            if key not in car_listings:
                car_listings[key] = 0
                car_days[key] = set()
            car_listings[key] += snap.listing_count
            car_days[key].add(snap.date)
        
        most_listed = []
        for (make, model), total_listings in car_listings.items():
            days_present = len(car_days[(make, model)])
            avg_listings = total_listings / days_present if days_present > 0 else 0
            most_listed.append({
                'make': make,
                'model': model,
                'avg_listings': round(avg_listings, 1),
                'days_present': days_present
            })
        
        most_listed.sort(key=lambda x: x['avg_listings'], reverse=True)
        
        return {
            'total_unique_cars': len(unique_cars),
            'avg_market_price': round(avg_price, 2) if avg_price else None,
            'total_snapshots': len(snapshots),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'most_listed': most_listed[:10]
        }
        
    finally:
        db.close()


if __name__ == "__main__":
    # Test the trends service
    print("Testing Trends Service...")
    print("=" * 80)
    
    print("\n1. Creating daily snapshot...")
    result = create_daily_snapshot()
    print(f"   Date: {result['date']}")
    print(f"   Created: {result['snapshots_created']}")
    print(f"   Updated: {result['snapshots_updated']}")
    print(f"   Total cars: {result['total_cars']}")
    
    if result['total_cars'] > 0:
        print("\n2. Getting market overview...")
        overview = get_market_overview(days=30)
        print(f"   Unique cars: {overview['total_unique_cars']}")
        print(f"   Avg market price: ${overview['avg_market_price']:,.0f}" if overview['avg_market_price'] else "   No price data")
        print(f"   Total snapshots: {overview['total_snapshots']}")
        
        if overview['most_listed']:
            print(f"\n3. Most listed cars:")
            for i, car in enumerate(overview['most_listed'][:5], 1):
                print(f"   {i}. {car['make']} {car['model']}: {car['avg_listings']} avg listings")
    else:
        print("\n⚠️  No data available yet. Run scrapers first!")

