import httpx


async def test_api_welcome_endpoint(client: httpx.AsyncClient):
    """Test the API welcome endpoint returns correct text message."""
    response = await client.get("/api/")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert response.text == "Welcome to Heroes of Talisman API"


async def test_api_welcome_endpoint_redirect(client: httpx.AsyncClient):
    """Test that /api redirects to /api/ and returns welcome message."""
    response = await client.get("/api", follow_redirects=True)

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert response.text == "Welcome to Heroes of Talisman API"


async def test_health_check_endpoint(client: httpx.AsyncClient):
    """Test the health check endpoint returns correct structure."""
    response = await client.get("/api/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "heroes-of-talisman"
    assert data["version"] == "0.1.0"
    assert "endpoints" in data
    assert data["endpoints"]["auth"] == "/api/auth"
    assert data["endpoints"]["health"] == "/api/health"


async def test_health_check_structure(client: httpx.AsyncClient):
    """Test that health check returns all required fields."""
    response = await client.get("/api/health")
    data = response.json()

    # Check all required fields are present
    required_fields = ["status", "service", "version", "endpoints"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Check endpoints structure
    assert isinstance(data["endpoints"], dict)
    assert "auth" in data["endpoints"]
    assert "health" in data["endpoints"]


async def test_nonexistent_endpoint(client: httpx.AsyncClient):
    """Test that nonexistent endpoints return 404."""
    response = await client.get("/api/nonexistent")

    assert response.status_code == 404


async def test_api_methods(client: httpx.AsyncClient):
    """Test that different HTTP methods are handled appropriately."""
    # GET should work for /api/health
    response = await client.get("/api/health")
    assert response.status_code == 200

    # POST should not be allowed for /api/health
    response = await client.post("/api/health")
    assert response.status_code == 405  # Method Not Allowed

    # PUT should not be allowed for /api/health
    response = await client.put("/api/health")
    assert response.status_code == 405  # Method Not Allowed

    # Test welcome endpoint with wrong methods
    response = await client.post("/api/")
    assert response.status_code == 405

    response = await client.put("/api/")
    assert response.status_code == 405

    response = await client.delete("/api/")
    assert response.status_code == 405
