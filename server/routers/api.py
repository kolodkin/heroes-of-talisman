from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel

from ..database import get_session
from ..models import Game, User
from ..auth import get_current_user

router = APIRouter(prefix="/api", tags=["api"])


class GameCreate(BaseModel):
    """Request model for creating a new game."""
    name: str
    game_id: Optional[str] = None


class GameResponse(BaseModel):
    """Response model for game information."""
    id: str
    name: str
    last_updated: str
    created: str
    connected_users: List[str]


@router.get("/", response_class=PlainTextResponse)
async def api_welcome():
    """Welcome message for the API."""
    return "Welcome to Heroes of Talisman API"


@router.get("/health")
async def health_check():
    """Health check endpoint returning status information."""
    return {
        "status": "healthy",
        "service": "heroes-of-talisman",
        "version": "0.1.0",
        "endpoints": {
            "auth": "/api/auth",
            "health": "/api/health",
            "websocket": "/ws/game/{game_id}/{user_id}?token=<jwt_token>"
        }
    }


@router.post("/games", response_model=GameResponse)
async def create_game(
    game_data: GameCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new game."""
    # Generate game ID if not provided
    result = await session.execute(select(Game))
    games = result.scalars().all()
    game_id = game_data.game_id or f"game_{len(games) + 1}"
    
    # Check if game ID already exists
    result = await session.execute(select(Game).where(Game.id == game_id))
    existing_game = result.first()
    if existing_game:
        raise HTTPException(status_code=400, detail="Game ID already exists")
    
    # Create new game
    game = Game(
        id=game_id,
        name=game_data.name,
        data={"users": {}, "game_state": "waiting"}
    )
    
    session.add(game)
    await session.commit()
    await session.refresh(game)
    
    return GameResponse(
        id=game.id,
        name=game.name,
        last_updated=game.last_updated.isoformat(),
        created=game.created.isoformat(),
        connected_users=[]
    )


@router.get("/games/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get game information."""
    result = await session.execute(select(Game).where(Game.id == game_id))
    game = result.first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # For now, return empty connected users since we're ignoring websocket parts
    connected_users = []
    
    return GameResponse(
        id=game.id,
        name=game.name,
        last_updated=game.last_updated.isoformat(),
        created=game.created.isoformat(),
        connected_users=connected_users
    )


@router.get("/games", response_model=List[GameResponse])
async def list_games(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List all games."""
    result = await session.execute(select(Game))
    games = result.scalars().all()
    
    # For now, return empty connected users since we're ignoring websocket parts
    return [
        GameResponse(
            id=game.id,
            name=game.name,
            last_updated=game.last_updated.isoformat(),
            created=game.created.isoformat(),
            connected_users=[]
        )
        for game in games
    ]


@router.delete("/games/{game_id}")
async def delete_game(
    game_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a game."""
    result = await session.execute(select(Game).where(Game.id == game_id))
    game = result.first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    await session.delete(game)
    await session.commit()
    
    return {"message": f"Game {game_id} deleted successfully"} 