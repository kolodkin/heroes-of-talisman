import pytest
import os
import asyncio
from typing import AsyncGenerator
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from server.main import app
from server.database import get_session
from server.models import User, Game
from server.auth import get_password_hash, create_access_token


# Test database configuration
def get_test_database_url():
    """Get test database URL."""
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_user = os.getenv("POSTGRES_USER", "postgres")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    
    return f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/pytest"


@pytest.fixture(scope="function")
async def async_session():
    """Create an async database session for direct async operations."""
    engine = create_async_engine(
        get_test_database_url(),
        pool_size=5,
        max_overflow=0,
        pool_pre_ping=True,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
        
        # Clean up after each test
        await session.rollback()
        await session.execute(text("DELETE FROM games"))
        await session.execute(text("DELETE FROM users"))
        await session.commit()
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def client(async_session: AsyncSession):
    """Create an async test client with dependency override."""
    
    async def override_get_session():
        """Override session for AsyncClient."""
        return async_session

    app.dependency_overrides[get_session] = override_get_session
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# For backwards compatibility, alias the fixtures
@pytest.fixture(name="session")
async def session_fixture(async_session):
    """Alias for async_session."""
    return async_session


@pytest.fixture(name="test_user")
async def test_user_fixture(async_session: AsyncSession):
    """Create a test user in the database."""
    user = User(
        email="test@example.com",
        password=get_password_hash("testpassword123")
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture(name="test_game")
async def test_game_fixture(async_session: AsyncSession):
    """Create a test game in the database."""
    game = Game(
        id="test-game-1",
        name="Test Game",
        data={"players": [], "status": "waiting"}
    )
    async_session.add(game)
    await async_session.commit()
    await async_session.refresh(game)
    return game


@pytest.fixture(name="auth_token")
def auth_token_fixture(test_user: User):
    """Create a JWT token for the test user."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str):
    """Create authorization headers with JWT token."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 