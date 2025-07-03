import os
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator


# Database configuration
def get_database_url():
    """Get database URL from environment variables."""
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_user = os.getenv("POSTGRES_USER", "postgres")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_db = os.getenv("POSTGRES_DB", "heroes_talisman")
    
    return f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

DATABASE_URL = os.getenv("DATABASE_URL", get_database_url())

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)


def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session for dependency injection."""
    with Session(engine) as session:
        yield session 