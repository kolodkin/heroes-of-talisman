import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from server.models import User
from server.auth import verify_password, verify_token


async def test_register_new_user(client: httpx.AsyncClient, session: AsyncSession):
    """Test successful user registration."""
    user_data = {"email": "newuser@example.com", "password": "newpassword123"}

    response = await client.post("/api/auth/register", json=user_data)

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "created_at" in data
    assert data["last_log_in"] is None
    assert "password" not in data  # Password should not be in response

    # Verify user was created in database
    result = await session.execute(select(User).where(User.email == user_data["email"]))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.email == user_data["email"]
    assert verify_password(user_data["password"], user.password)


async def test_register_duplicate_email(client: httpx.AsyncClient, test_user: User):
    """Test registration with existing email fails."""
    user_data = {"email": test_user.email, "password": "newpassword123"}

    response = await client.post("/api/auth/register", json=user_data)

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


async def test_register_invalid_email(client: httpx.AsyncClient):
    """Test registration with invalid email format."""
    user_data = {"email": "invalid-email", "password": "password123"}

    response = await client.post("/api/auth/register", json=user_data)

    assert response.status_code == 422


async def test_register_missing_fields(client: httpx.AsyncClient):
    """Test registration with missing required fields."""
    # Missing password
    response = await client.post("/api/auth/register", json={"email": "test@example.com"})
    assert response.status_code == 422

    # Missing email
    response = await client.post("/api/auth/register", json={"password": "password123"})
    assert response.status_code == 422

    # Empty request
    response = await client.post("/api/auth/register", json={})
    assert response.status_code == 422


async def test_login_valid_credentials(client: httpx.AsyncClient, test_user: User):
    """Test successful login with valid credentials."""
    login_data = {"email": test_user.email, "password": "testpassword123"}

    response = await client.post("/api/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0

    # Verify token is valid
    email = verify_token(data["access_token"])
    assert email == test_user.email


async def test_login_invalid_email(client: httpx.AsyncClient):
    """Test login with nonexistent email."""
    login_data = {"email": "nonexistent@example.com", "password": "password123"}

    response = await client.post("/api/auth/login", json=login_data)

    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


async def test_login_invalid_password(client: httpx.AsyncClient, test_user: User):
    """Test login with incorrect password."""
    login_data = {"email": test_user.email, "password": "wrongpassword"}

    response = await client.post("/api/auth/login", json=login_data)

    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


async def test_login_missing_fields(client: httpx.AsyncClient):
    """Test login with missing required fields."""
    # Missing password
    response = await client.post("/api/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 422

    # Missing email
    response = await client.post("/api/auth/login", json={"password": "password123"})
    assert response.status_code == 422


async def test_login_updates_last_login(client: httpx.AsyncClient, test_user: User, session: AsyncSession):
    """Test that login updates the last_log_in timestamp."""
    login_data = {"email": test_user.email, "password": "testpassword123"}

    # User should not have last_log_in initially
    assert test_user.last_log_in is None

    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200

    # Check that last_log_in was updated
    await session.refresh(test_user)
    assert test_user.last_log_in is not None


async def test_get_current_user_with_valid_token(client: httpx.AsyncClient, test_user: User, auth_headers: dict):
    """Test accessing protected endpoint with valid JWT token."""
    response = await client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert "created_at" in data
    assert "password" not in data


async def test_get_current_user_without_token(client: httpx.AsyncClient):
    """Test accessing protected endpoint without token."""
    response = await client.get("/api/auth/me")

    assert response.status_code == 403
    assert "Not authenticated" in response.json()["detail"]


async def test_get_current_user_with_invalid_token(client: httpx.AsyncClient):
    """Test accessing protected endpoint with invalid token."""
    headers = {"Authorization": "Bearer invalid-token"}
    response = await client.get("/api/auth/me", headers=headers)

    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


async def test_get_current_user_with_expired_token(client: httpx.AsyncClient, test_user: User):
    """Test accessing protected endpoint with expired token."""
    from datetime import datetime, timedelta, timezone
    from server.auth import jwt, SECRET_KEY, ALGORITHM

    # Create expired token
    expired_payload = {"sub": test_user.email, "exp": datetime.now(timezone.utc) - timedelta(minutes=30)}
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await client.get("/api/auth/me", headers=headers)

    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


async def test_get_current_user_with_malformed_bearer_token(client: httpx.AsyncClient):
    """Test accessing protected endpoint with malformed bearer token."""
    headers = {"Authorization": "Bearer"}
    response = await client.get("/api/auth/me", headers=headers)

    assert response.status_code == 403


async def test_get_current_user_with_different_auth_scheme(client: httpx.AsyncClient, auth_token: str):
    """Test accessing protected endpoint with different auth scheme."""
    headers = {"Authorization": f"Basic {auth_token}"}
    response = await client.get("/api/auth/me", headers=headers)

    assert response.status_code == 403
    assert "Invalid authentication credentials" in response.json()["detail"]


async def test_complete_auth_flow(client: httpx.AsyncClient, session: AsyncSession):
    """Test complete registration -> login -> access protected endpoint flow."""
    # 1. Register new user
    user_data = {"email": "flowtest@example.com", "password": "flowtest123"}

    register_response = await client.post("/api/auth/register", json=user_data)
    assert register_response.status_code == 200

    # 2. Login with new user
    login_response = await client.post("/api/auth/login", json=user_data)
    assert login_response.status_code == 200

    token_data = login_response.json()
    assert "access_token" in token_data

    # 3. Access protected endpoint
    auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_response = await client.get("/api/auth/me", headers=auth_headers)
    assert me_response.status_code == 200

    user_info = me_response.json()
    assert user_info["email"] == user_data["email"]
