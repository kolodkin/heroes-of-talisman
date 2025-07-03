import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from server.models import User
from server.auth import verify_password, verify_token


class TestUserRegistration:
    """Test user registration functionality."""
    
    def test_register_new_user(self, client: TestClient, session: Session):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "created_at" in data
        assert data["last_log_in"] is None
        assert "password" not in data  # Password should not be in response
        
        # Verify user was created in database
        user = session.exec(select(User).where(User.email == user_data["email"])).first()
        assert user is not None
        assert user.email == user_data["email"]
        assert verify_password(user_data["password"], user.password)
    
    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with existing email fails."""
        user_data = {
            "email": test_user.email,
            "password": "newpassword123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email format."""
        user_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422
    
    def test_register_missing_fields(self, client: TestClient):
        """Test registration with missing required fields."""
        # Missing password
        response = client.post("/api/auth/register", json={"email": "test@example.com"})
        assert response.status_code == 422
        
        # Missing email
        response = client.post("/api/auth/register", json={"password": "password123"})
        assert response.status_code == 422
        
        # Empty request
        response = client.post("/api/auth/register", json={})
        assert response.status_code == 422


class TestUserLogin:
    """Test user login functionality."""
    
    def test_login_valid_credentials(self, client: TestClient, test_user: User):
        """Test successful login with valid credentials."""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        
        # Verify token is valid
        email = verify_token(data["access_token"])
        assert email == test_user.email
    
    def test_login_invalid_email(self, client: TestClient):
        """Test login with nonexistent email."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """Test login with incorrect password."""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing required fields."""
        # Missing password
        response = client.post("/api/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422
        
        # Missing email
        response = client.post("/api/auth/login", json={"password": "password123"})
        assert response.status_code == 422
    
    def test_login_updates_last_login(self, client: TestClient, test_user: User, session: Session):
        """Test that login updates the last_log_in timestamp."""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        # User should not have last_log_in initially
        assert test_user.last_log_in is None
        
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        
        # Check that last_log_in was updated
        session.refresh(test_user)
        assert test_user.last_log_in is not None


class TestProtectedEndpoints:
    """Test protected endpoints requiring authentication."""
    
    def test_get_current_user_with_valid_token(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test accessing protected endpoint with valid JWT token."""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert "created_at" in data
        assert "password" not in data
    
    def test_get_current_user_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_current_user_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_get_current_user_with_expired_token(self, client: TestClient, test_user: User):
        """Test accessing protected endpoint with expired token."""
        from datetime import datetime, timedelta, timezone
        from server.auth import jwt, SECRET_KEY, ALGORITHM
        
        # Create expired token
        expired_payload = {
            "sub": test_user.email,
            "exp": datetime.now(timezone.utc) - timedelta(minutes=30)
        }
        expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_get_current_user_with_malformed_bearer_token(self, client: TestClient):
        """Test accessing protected endpoint with malformed bearer token."""
        headers = {"Authorization": "Bearer"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 403
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_current_user_with_different_auth_scheme(self, client: TestClient, auth_token: str):
        """Test accessing protected endpoint with different auth scheme."""
        headers = {"Authorization": f"Basic {auth_token}"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 403
        assert "Invalid authentication credentials" in response.json()["detail"]


class TestAuthFlow:
    """Test complete authentication flow."""
    
    def test_complete_auth_flow(self, client: TestClient, session: Session):
        """Test complete registration -> login -> access protected endpoint flow."""
        # 1. Register new user
        user_data = {
            "email": "flowtest@example.com",
            "password": "flowtest123"
        }
        
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 200
        
        # 2. Login with new user
        login_response = client.post("/api/auth/login", json=user_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        assert "access_token" in token_data
        
        # 3. Access protected endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        me_response = client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        user_info = me_response.json()
        assert user_info["email"] == user_data["email"] 