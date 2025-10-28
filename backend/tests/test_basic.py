"""
Phase 0 Tests - Basic Setup Validation
"""
import pytest


def test_imports():
    """Verify core libraries are importable"""
    import fastapi
    import uvicorn
    assert True


def test_app_exists():
    """Verify FastAPI app exists and is configured"""
    from main import app
    assert app is not None
    assert app.title == "Cars Trends API"
    # Version changes as we add features
    assert app.version is not None


def test_root_endpoint():
    """Test the root endpoint returns correct response"""
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data
    assert "phase" in data  # Phase number changes as we progress


def test_health_endpoint():
    """Test the health check endpoint"""
    from fastapi.testclient import TestClient
    from main import app
    
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["api_version"] == "0.1.0"

