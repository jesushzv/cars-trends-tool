"""
Tests for Phase 14: Scheduling
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.scheduler_service import (
    initialize_scheduler,
    start_scheduler,
    stop_scheduler,
    get_scheduler_status,
    get_jobs
)


class TestSchedulerInitialization:
    """Test scheduler initialization"""
    
    def test_initialize_scheduler(self):
        """Test that scheduler can be initialized"""
        scheduler = initialize_scheduler()
        assert scheduler is not None
    
    def test_scheduler_has_jobs(self):
        """Test that scheduler has configured jobs"""
        initialize_scheduler()
        jobs = get_jobs()
        
        # Should have 4 jobs: 3 scrapers + 1 snapshot
        assert len(jobs) >= 4
        
        # Check job IDs exist
        job_ids = [job['id'] for job in jobs]
        assert 'scrape_craigslist' in job_ids
        assert 'scrape_mercadolibre' in job_ids
        assert 'scrape_facebook' in job_ids
        assert 'daily_snapshot' in job_ids
    
    def test_job_structure(self):
        """Test that jobs have correct structure"""
        initialize_scheduler()
        jobs = get_jobs()
        
        for job in jobs:
            assert 'id' in job
            assert 'name' in job
            assert 'trigger' in job
            # next_run may be None before starting
            assert 'next_run' in job


class TestSchedulerControl:
    """Test scheduler start/stop"""
    
    def test_start_scheduler(self):
        """Test starting the scheduler"""
        result = start_scheduler()
        
        assert 'status' in result
        assert result['status'] in ['started', 'already_running']
    
    def test_stop_scheduler(self):
        """Test stopping the scheduler"""
        # Start first to ensure it's running
        start_scheduler()
        
        result = stop_scheduler()
        assert 'status' in result
        assert result['status'] == 'stopped'
    
    def test_scheduler_status(self):
        """Test getting scheduler status"""
        status = get_scheduler_status()
        
        assert 'running' in status
        assert 'message' in status
        assert 'jobs' in status
        assert isinstance(status['running'], bool)
        assert isinstance(status['jobs'], list)


class TestSchedulerAPI:
    """Test scheduler API integration"""
    
    def test_scheduler_endpoints_exist(self):
        """Test that scheduler endpoints are registered"""
        from main import app
        
        routes = [route.path for route in app.routes]
        
        assert '/scheduler/status' in routes
        assert '/scheduler/start' in routes
        assert '/scheduler/stop' in routes
        assert '/scheduler/trigger/{job_id}' in routes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

