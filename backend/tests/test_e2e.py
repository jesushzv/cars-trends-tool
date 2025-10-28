"""
End-to-End Tests
Phase 19: CI/CD Pipeline

Tests critical user flows from start to finish.
These tests ensure the main features work together correctly.

NOTE: These tests use the actual SQLite database (listings.db).
They test that the API endpoints are working correctly.
"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestCriticalUserFlows:
    """Test critical end-to-end user flows"""
    
    def test_auth_endpoints_exist(self, client):
        """
        E2E Test: Authentication endpoints are accessible
        """
        # Register endpoint exists (may fail if user exists, that's ok)
        response = client.post(
            "/auth/register",
            params={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpass123"
            }
        )
        # Should be 200 (success) or 400 (already exists)
        assert response.status_code in [200, 400]
        
        # Login endpoint requires credentials
        response = client.post(
            "/auth/login",
            params={
                "username": "fakeuser",
                "password": "wrongpass"
            }
        )
        # Should be 401 (unauthorized)
        assert response.status_code == 401
        
        # Protected endpoint requires auth
        response = client.get("/auth/me")
        assert response.status_code == 401
    
    def test_api_health_check(self, client):
        """
        E2E Test: Basic API health
        Verify all critical endpoints respond
        """
        # Root endpoint
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        
        # Listings endpoint (returns dict with 'listings' key)
        response = client.get("/listings")
        assert response.status_code == 200
        data = response.json()
        # Can be list (old format) or dict with 'listings' key (new format)
        assert isinstance(data, (list, dict))
        
        # Analytics endpoints
        response = client.get("/analytics/top-cars")
        assert response.status_code == 200
        
        response = client.get("/analytics/summary")
        assert response.status_code == 200
    
    def test_scheduler_integration(self, client):
        """
        E2E Test: Scheduler endpoints
        Verify scheduler can be controlled via API
        """
        # Get scheduler status
        response = client.get("/scheduler/status")
        assert response.status_code == 200
        status = response.json()
        assert "running" in status
        assert "jobs" in status
        # Jobs may or may not be present depending on scheduler state
        assert isinstance(status["jobs"], list)
    
    def test_trends_workflow(self, client):
        """
        E2E Test: Trends and analytics workflow
        Verify endpoints respond correctly
        """
        # Market overview
        response = client.get("/trends/overview")
        assert response.status_code == 200
        overview = response.json()
        assert isinstance(overview, (dict, list))
        
        # Trending cars (may return dict or list depending on data)
        response = client.get("/trends/trending")
        assert response.status_code == 200
        trending = response.json()
        assert isinstance(trending, (dict, list))
    
    def test_error_handling(self, client):
        """
        E2E Test: Error handling
        Verify API handles errors gracefully
        """
        # 404 for non-existent endpoint
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # 401 for auth required
        response = client.get("/auth/me")
        assert response.status_code == 401
        
        # 400 for invalid login
        response = client.post(
            "/auth/login",
            params={"username": "fake", "password": "wrong"}
        )
        assert response.status_code == 401


class TestDataIntegrity:
    """Test data flows and integrity"""
    
    def test_database_connectivity(self, client):
        """
        E2E Test: Database operations
        Verify database is accessible through API
        """
        # Test that analytics endpoints can query database
        response = client.get("/analytics/summary")
        assert response.status_code == 200
        summary = response.json()
        assert isinstance(summary, dict)


@pytest.mark.slow
class TestPerformance:
    """Basic performance tests"""
    
    def test_api_response_time(self, client):
        """
        E2E Test: API performance
        Verify API responds quickly
        """
        import time
        
        # Test root endpoint
        start = time.time()
        response = client.get("/")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond in < 1 second
    
    def test_multiple_concurrent_requests(self, client):
        """
        E2E Test: Concurrent requests
        Verify API handles multiple simultaneous requests
        """
        import concurrent.futures
        
        def make_request():
            response = client.get("/")
            return response.status_code
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])

