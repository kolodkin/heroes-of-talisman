import logging
import asyncio
import json
from http import HTTPStatus
from pathlib import Path

from fastapi import APIRouter, FastAPI, WebSocket, HTTPException, WebSocketDisconnect, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse, FileResponse
import uvicorn
from redis.asyncio import Redis
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from .env import REDIS_HOST, REDIS_PORT
from .game_engine import GameEngine
from .gameplay.models import DEFAULT_GAME, GamePlay, StageName
from .gameplay.debug_presets import get_debug_preset, DEBUG_PRESETS
from .db_models import Game as GameTable
from .database import get_db, AsyncSessionLocal

logger = logging.getLogger("uvicorn")

app = FastAPI()
router = APIRouter()

# Set up CORS
origins = [
    "*",
    # "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis client (for pub/sub only)
redis_client = Redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")


# Static files directory for SPA
STATIC_DIR = Path(__file__).parent / "www"


@app.get("/health")
async def health():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(select(1))
        db_status = "up"
    except Exception as e:
        db_status = f"down {session.bind.url} - {e.__class__.__name__}:{e}"

    # Check Redis connection
    try:
        await redis_client.ping()
        redis_status = "up"
    except Exception as e:
        redis_status = f"down {REDIS_HOST}:{REDIS_PORT} - {e.__class__.__name__}:{e}"
    return {
        "db": db_status,
        "redis": redis_status,
    }


class Game(BaseModel):
    name: str


class PresetGame(BaseModel):
    name: str
    preset: DEBUG_PRESETS
    stage: StageName | None = None


@router.post("/")
async def add_game(new_game: Game, session: AsyncSession = Depends(get_db)):
    if len(new_game.name) == 0:
        raise HTTPException(status_code=400, detail="Game name cannot be empty")

    # Check if game already exists
    result = await session.execute(select(GameTable).where(GameTable.name == new_game.name))
    existing_game = result.scalar_one_or_none()

    if existing_game:
        raise HTTPException(status_code=400, detail="Game already exists")

    # Create new game with default data
    game_data = DEFAULT_GAME.db_model_dump()
    db_game = GameTable(name=new_game.name, data=game_data)

    session.add(db_game)
    await session.commit()

    return {"message": "Game added successfully"}


@router.post("/preset_games")
async def add_preset_game(preset_game: PresetGame, session: AsyncSession = Depends(get_db)):
    if len(preset_game.name) == 0:
        raise HTTPException(status_code=400, detail="Game name cannot be empty")

    # Check if game already exists
    result = await session.execute(select(GameTable).where(GameTable.name == preset_game.name))
    existing_game = result.scalar_one_or_none()

    if existing_game:
        raise HTTPException(status_code=400, detail="Game already exists")

    # Create new game with preset data
    game_data = get_debug_preset(preset_game.preset, preset_game.stage)
    db_game = GameTable(name=preset_game.name, data=game_data.db_model_dump())

    session.add(db_game)
    await session.commit()

    return {"message": "Preset game added successfully"}


@router.get("/")
async def get_games(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(GameTable.name))
    games = result.scalars().all()
    return list(games)


@router.delete("/{gamename}")
async def delete_game(gamename: str, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(GameTable).where(GameTable.name == gamename))
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")

    await session.delete(game)
    await session.commit()
    return {"message": "Game deleted successfully"}


@router.post("/{gamename}/reset")
async def reset_game(gamename: str, session: AsyncSession = Depends(get_db)):
    redis_meta = RedisMeta(gamename)

    result = await session.execute(select(GameTable).where(GameTable.name == gamename))
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")

    # Reset game data to default
    game.data = DEFAULT_GAME.db_model_dump()
    await session.commit()

    # Notify connected clients
    await redis_client.publish(redis_meta.channel, json.dumps(dict(event="game_update")))

    return {"message": "Game reset successfully"}


@app.post("/check-game-name")
async def check_game_name(game: Game, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(GameTable).where(GameTable.name == game.name))
    existing_game = result.scalar_one_or_none()
    is_unique = existing_game is None
    return {"isUnique": is_unique}


class RedisMeta:
    def __init__(self, gamename: str, username: str = None):
        self.gamename = gamename
        self.username = username

    @property
    def channel(self):
        return f"game:{self.gamename}-event"

    @property
    def key(self):
        return f"game:{self.gamename}"


async def from_database_locked(session: AsyncSession, redis_meta: RedisMeta) -> tuple[GameEngine, GameTable]:
    """Load game from database with row lock for updates"""
    result = await session.execute(select(GameTable).where(GameTable.name == redis_meta.gamename).with_for_update())
    game_db = result.scalar_one_or_none()

    if game_db is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")

    game_model = GamePlay.model_validate(game_db.data)
    if redis_meta.username is None:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="missing username")

    return GameEngine(redis_meta.gamename, redis_meta.username, game_model), game_db


async def from_database(session: AsyncSession, redis_meta: RedisMeta) -> GameEngine:
    """Load game from database without lock for reading"""
    result = await session.execute(select(GameTable).where(GameTable.name == redis_meta.gamename))
    game = result.scalar_one_or_none()

    if game is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")

    game_model = GamePlay.model_validate(game.data)
    if redis_meta.username is None:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="missing username")

    return GameEngine(redis_meta.gamename, redis_meta.username, game_model)


async def game_update_loop(websocket: WebSocket, redis_meta: RedisMeta):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(redis_meta.channel)
    logger.info(f"User '{redis_meta.username}' subscribed to channel '{redis_meta.channel}'")
    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            if data["event"] == "game_update":
                event_action = data.get("event_action", "unknown")
                logger.info(f"User '{redis_meta.username}' received game_update event from action '{event_action}'")
                async with AsyncSessionLocal() as session:
                    game_engine = await from_database(session, redis_meta)
                    await websocket.send_json(
                        {
                            "event": "game_update",
                            "event_action": event_action,
                            "game": game_engine.model_dump(),
                        }
                    )
            else:
                logger.warning(f"Unknown event: {data}")


async def actions_loop(websocket: WebSocket, redis_meta: RedisMeta):
    while True:
        action = await websocket.receive_text()
        action = json.loads(action)
        logger.info(f"Received action: {action}")

        success = False
        action_name = None
        async with AsyncSessionLocal() as session:
            try:
                if "action" not in action:
                    raise GameException("Missing 'action' field")

                action_name = action["action"]
                game_engine, game_db = await from_database_locked(session, redis_meta)
                game_engine.action(action)
                success = True
            except Exception as e:
                logger.warning(f"Error processing action. action: {action}", exc_info=e)
                await websocket.send_json({"error": str(e), "class": e.__class__.__name__})

            if not success:
                continue

            logger.info(f"Sending game state to user '{game_engine.username}'")

            # Save to database (game_db is already locked)
            game_db.data = game_engine.game.db_model_dump()
            await session.commit()

        # Notify connected clients (outside session context)
        logger.info(f"Publishing game_update event to channel '{redis_meta.channel}'")
        await redis_client.publish(redis_meta.channel, json.dumps(dict(event="game_update", event_action=action_name)))


@app.websocket("/ws/{gamename}/{username}")
async def ws_game_endpoint(websocket: WebSocket, gamename: str, username: str):
    redis_meta = RedisMeta(gamename, username)

    await websocket.accept()

    # Check if game exists in database
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(GameTable).where(GameTable.name == gamename))
        game = result.scalar_one_or_none()

        if not game:
            await websocket.send_json({"error": "Game not found"})
            await websocket.close()
            return

    logger.info(f"Connection to game {gamename} established for user {username}")
    try:
        await asyncio.gather(
            game_update_loop(websocket, redis_meta),
            actions_loop(websocket, redis_meta),
        )
    except WebSocketDisconnect:
        async with AsyncSessionLocal() as session:
            game_engine, game_db = await from_database_locked(session, redis_meta)
            game_engine.run_action("disconnect")

            # Save to database
            game_db.data = game_engine.game.db_model_dump()
            await session.commit()

            # Notify connected clients
            await redis_client.publish(redis_meta.channel, json.dumps(dict(event="game_update")))

        logger.info(f"Client '{username}' disconnected from game '{gamename}'")
    finally:
        # Perform any cleanup actions here
        logger.info(f"Connection to game '{gamename}' closed for user '{username}'")


app.include_router(router, prefix="/api/games", tags=["games"])

# Mount static files for SPA (must come after API routes to avoid conflicts)
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")
    app.mount("/images", StaticFiles(directory=STATIC_DIR / "images"), name="images")


async def spa_index():
    """Helper to serve index.html for SPA routing"""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return PlainTextResponse("SPA not built. Run scripts/build.sh first.", status_code=404)


# SPA routes - serve index.html for client-side routing
@app.get("/")
async def spa_home():
    """Serve index.html for home page"""
    return await spa_index()


@app.get("/games/{gamename}/{playername}")
async def spa_game_page(gamename: str, playername: str):
    """Serve index.html for game page"""
    return await spa_index()


if __name__ == "__main__":
    port = os.getenv("APP_PORT", 8000)
    uvicorn.run(app, host="0.0.0.0", port=port)
