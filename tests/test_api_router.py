import pytest
from fastapi.testclient import TestClient


def test_api_welcome_endpoint(client: TestClient):
    """Test the API welcome endpoint returns correct text message."""
    response = client.get("/api/")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert response.text == "Welcome to Heroes of Talisman Game Engine API"


def test_api_welcome_endpoint_redirect(client: TestClient):
    """Test that /api redirects to /api/ and returns welcome message."""
    response = client.get("/api", follow_redirects=True)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert response.text == "Welcome to Heroes of Talisman Game Engine API"


def test_health_check_endpoint(client: TestClient):
    """Test the health check endpoint returns correct structure."""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "heroes-of-talisman"
    assert data["version"] == "0.1.0"
    assert "endpoints" in data
    assert data["endpoints"]["auth"] == "/api/auth"
    assert data["endpoints"]["health"] == "/api/health"


def test_health_check_structure(client: TestClient):
    """Test that health check returns all required fields."""
    response = client.get("/api/health")
    data = response.json()
    
    # Check all required fields are present
    required_fields = ["status", "service", "version", "endpoints"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Check endpoints structure
    assert isinstance(data["endpoints"], dict)
    assert "auth" in data["endpoints"]
    assert "health" in data["endpoints"]


def test_nonexistent_endpoint(client: TestClient):
    """Test that nonexistent endpoints return 404."""
    response = client.get("/api/nonexistent")
    
    assert response.status_code == 404


def test_api_methods(client: TestClient):
    """Test that API endpoints only respond to correct HTTP methods."""
    # Test welcome endpoint with wrong methods
    response = client.post("/api/")
    assert response.status_code == 405
    
    response = client.put("/api/")
    assert response.status_code == 405
    
    response = client.delete("/api/")
    assert response.status_code == 405
    
    # Test health endpoint with wrong methods
    response = client.post("/api/health")
    assert response.status_code == 405
    
    response = client.put("/api/health")
    assert response.status_code == 405
    
    response = client.delete("/api/health")
    assert response.status_code == 405 