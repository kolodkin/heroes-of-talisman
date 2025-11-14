import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from server.main import app
from server.database import get_db
from server.db_models import Game as GameTable


# Import environment variables
from server.env import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT

# Build test database URL with separate test_db database
TEST_DB_NAME = "test_db"
TEST_DB_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{TEST_DB_NAME}"

# Create URL to default postgres database for creating/dropping test_db
POSTGRES_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"

# Create synchronous test database engine
test_engine = create_engine(TEST_DB_URL, echo=False)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
)


class AsyncSessionWrapper:
    """Wrapper to make sync session work with async code"""

    def __init__(self, sync_session):
        self._sync_session = sync_session

    async def execute(self, stmt):
        """Convert sync execute to async"""
        return self._sync_session.execute(stmt)

    async def commit(self):
        """Convert sync commit to async"""
        return self._sync_session.commit()

    async def close(self):
        """Convert sync close to async"""
        return self._sync_session.close()

    def add(self, instance):
        """Passthrough sync add"""
        return self._sync_session.add(instance)

    async def delete(self, instance):
        """Convert sync delete to async"""
        return self._sync_session.delete(instance)

    def __getattr__(self, name):
        """Fallback to sync session for other methods"""
        return getattr(self._sync_session, name)


def get_test_db():
    """Override database dependency for testing - returns async-compatible session"""
    try:
        sync_db = TestSessionLocal()
        async_db = AsyncSessionWrapper(sync_db)
        yield async_db
    finally:
        sync_db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database once for all tests"""
    # Connect to default postgres database to create/drop test_db
    postgres_engine = create_engine(POSTGRES_URL, isolation_level="AUTOCOMMIT", echo=False)

    with postgres_engine.connect() as conn:
        # Drop test database if it exists
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        # Create fresh test database using template0 to avoid collation mismatch
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME} TEMPLATE template0"))

    postgres_engine.dispose()

    # Create tables in test database
    SQLModel.metadata.create_all(test_engine)

    yield

    # Note: Not dropping test_db after tests for debugging purposes
    # The database will be dropped and recreated on the next test run


@pytest.fixture(scope="function")
def client():
    """Create test client with database dependency override"""
    # Override dependency
    app.dependency_overrides[get_db] = get_test_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def gamename(request):
    """Generate unique game name and clean up after test"""
    name = f"test-{request.node.name}"
    yield name

    # Clean up this specific game and any games with this name as prefix after the test
    with TestSessionLocal() as session:
        session.execute(GameTable.__table__.delete().where(GameTable.name.like(f"{name}%")))
        session.commit()
