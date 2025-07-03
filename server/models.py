from datetime import datetime
from typing import Optional, Any, Dict
from sqlmodel import SQLModel, Field, Column, JSON
from pydantic import EmailStr


class User(SQLModel, table=True):
    """User model for authentication and game access."""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    password: str = Field(min_length=8)
    last_log_in: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Game(SQLModel, table=True):
    """Game model storing game state and metadata."""
    __tablename__ = "games"
    
    id: str = Field(primary_key=True)
    name: str = Field(min_length=1, max_length=100)
    data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created: datetime = Field(default_factory=datetime.utcnow) 