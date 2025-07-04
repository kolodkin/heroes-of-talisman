import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from server.main import app
from server.database import get_session
from server.models import User, Game
from server.auth import get_password_hash, create_access_token


# Test database configuration
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database session override."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user in the database."""
    user = User(email="test@example.com", password=get_password_hash("testpassword123"))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_game")
def test_game_fixture(session: Session):
    """Create a test game in the database."""
    game = Game(id="test-game-1", name="Test Game", data={"players": [], "status": "waiting"})
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


@pytest.fixture(name="auth_token")
def auth_token_fixture(test_user: User):
    """Create a JWT token for the test user."""
    token = create_access_token(data={"sub": test_user.email})
    return token


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str):
    """Create authorization headers with JWT token."""
    return {"Authorization": f"Bearer {auth_token}"}
