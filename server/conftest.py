import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from server.main import app
from server.database import get_db
from server.db_models import Game as GameTable


# Set test database environment variable to match setup.sh
os.environ["POSTGRES_DB"] = "test_db"

# Import the updated database URL after setting the env var
from server.env import DB_URL


# Create synchronous test database engine
test_engine = create_engine(DB_URL, echo=False)

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
    # Create tables once at start using sync engine
    SQLModel.metadata.create_all(test_engine)
    yield
    # Clean up is handled by setup script


@pytest.fixture(scope="function")
def client():
    """Create test client with database dependency override"""
    # Clear any existing data
    with TestSessionLocal() as session:
        # Delete all games before each test
        session.execute(GameTable.__table__.delete())
        session.commit()

    # Override dependency
    app.dependency_overrides[get_db] = get_test_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()
