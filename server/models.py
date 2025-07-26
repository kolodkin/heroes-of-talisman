from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, text
from sqlalchemy.dialects.postgresql import JSONB


class Game(SQLModel, table=True):
    __tablename__ = "games"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    data: Optional[bytes] = None
    chat: Optional[dict] = Field(default={}, sa_type=JSONB)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")))

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
