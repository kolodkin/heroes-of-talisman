import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from sqlalchemy import create_engine, text
from sqlmodel import SQLModel
from typing import AsyncGenerator


# Database configuration
def get_database_url(lib="asyncpg"):
    """Get database URL from environment variables."""
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_user = os.getenv("POSTGRES_USER", "postgres")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_db = os.getenv("POSTGRES_DB", "talisengine")

    return f"postgresql+{lib}://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"


def get_pg_connection_url(lib="asyncpg"):
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_user = os.getenv("POSTGRES_USER", "postgres")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")

    return f"postgresql+{lib}://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}"


DATABASE_URL = os.getenv("DATABASE_URL", get_database_url())

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    echo=os.getenv("DEBUG", "false").lower() == "true",
)

# Create session factory
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    """Create database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    async with SessionLocal() as session:
        yield session


def pg_create_database() -> None:
    """Create a database if it doesn't exist."""
    engine = create_engine(get_pg_connection_url(lib="psycopg2"))
    # Disable autocommit to handle database creation manually
    db_name = os.getenv("POSTGRES_DB", "talisengine")
    connection = engine.connect().execution_options(isolation_level="AUTOCOMMIT")
    # First check if database exists
    result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))

    # Create if it doesn't exist
    if not result.scalar():
        connection.execute(text(f"CREATE DATABASE {db_name}"))

    connection.close()


if __name__ == "__main__":
    pg_create_database()
