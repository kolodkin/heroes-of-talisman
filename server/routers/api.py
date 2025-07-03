from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlmodel import Session, select
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
    """API welcome endpoint returning text message as per design guidelines."""
    return "Welcome to Heroes of Talisman Game Engine API"


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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new game."""
    # Generate game ID if not provided
    game_id = game_data.game_id or f"game_{len(session.exec(select(Game)).all()) + 1}"
    
    # Check if game ID already exists
    existing_game = session.exec(select(Game).where(Game.id == game_id)).first()
    if existing_game:
        raise HTTPException(status_code=400, detail="Game ID already exists")
    
    # Create new game
    game = Game(
        id=game_id,
        name=game_data.name,
        data={"users": {}, "game_state": "waiting"}
    )
    
    session.add(game)
    session.commit()
    session.refresh(game)
    
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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get game information."""
    game = session.exec(select(Game).where(Game.id == game_id)).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get connected users from WebSocket manager
    from ..websocket import manager
    connected_users = manager.get_connected_users(game_id)
    
    return GameResponse(
        id=game.id,
        name=game.name,
        last_updated=game.last_updated.isoformat(),
        created=game.created.isoformat(),
        connected_users=connected_users
    )


@router.get("/games", response_model=List[GameResponse])
async def list_games(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List all games."""
    games = session.exec(select(Game)).all()
    
    # Get connected users from WebSocket manager
    from ..websocket import manager
    
    return [
        GameResponse(
            id=game.id,
            name=game.name,
            last_updated=game.last_updated.isoformat(),
            created=game.created.isoformat(),
            connected_users=manager.get_connected_users(game.id)
        )
        for game in games
    ]


@router.delete("/games/{game_id}")
async def delete_game(
    game_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a game."""
    game = session.exec(select(Game).where(Game.id == game_id)).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    session.delete(game)
    session.commit()
    
    return {"message": f"Game {game_id} deleted successfully"} 