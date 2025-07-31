from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import event


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Game(SQLModel, table=True):
    __tablename__ = "games"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    data: Optional[bytes] = Field(default=None, sa_type=JSONB, nullable=True)
    chat: Optional[dict] = Field(default={}, sa_type=JSONB)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


# Auto-update `updated_at` on update
@event.listens_for(Game, "before_update", propagate=True)
def set_updated_at(mapper, connection, target):
    target.updated_at = utc_now()
