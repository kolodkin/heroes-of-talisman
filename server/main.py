import logging
import json

from fastapi import APIRouter, FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
import uvicorn
from redis.asyncio import Redis

from .game_engine import __DEFAULT_GAME__, GameEngine

logger = logging.getLogger("uvicorn")

app = FastAPI()
router = APIRouter()

# Set up CORS
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis client
redis_client = Redis.from_url("redis://localhost")


@app.get("/")
async def root():
    return PlainTextResponse("Welcome to 'Heroes of Talisman' game server!")


@app.get("/health")
async def health():
    return PlainTextResponse("Server is up")


class Game(BaseModel):
    name: str


@router.post("/")
async def add_game(game: Game):
    if len(game.name) == 0:
        raise HTTPException(status_code=400, detail="Game name cannot be empty")

    if await redis_client.exists(f"game:{game.name}"):
        raise HTTPException(status_code=400, detail="Game name already exists")

    await redis_client.rpush("games", game.name)
    await redis_client.set(f"game:{game.name}", json.dumps(__DEFAULT_GAME__))

    return {"message": "Game added successfully"}


@router.get("/")
async def get_games():
    games = await redis_client.lrange("games", 0, -1)
    return [game.decode("utf-8") for game in games]


@router.delete("/{game_name}")
async def delete_game(game_name: str):
    if not await redis_client.exists(f"game:{game_name}"):
        raise HTTPException(status_code=404, detail="Game not found")
    await redis_client.lrem("games", 0, game_name)
    await redis_client.delete(f"game:{game_name}")
    return {"message": "Game deleted successfully"}


@app.post("/check-game-name")
async def check_game_name(game: Game):
    is_unique = not await redis_client.exists(f"game:{game.name}")
    return {"isUnique": is_unique}


@app.websocket("/ws/{game_name}/{username}")
async def websocket_endpoint(websocket: WebSocket, game_name: str, username: str):
    if not await redis_client.exists(f"game:{game_name}"):
        raise HTTPException(status_code=404, detail="Game not found")

    await websocket.accept()
    logger.info(f"Connection to game {game_name} established for user {username}")
    try:
        while True:
            action = await websocket.receive_text()
            action = json.loads(action)
            logger.info(f"Received action: {action}")

            game = await redis_client.get(f"game:{game_name}")
            game = json.loads(game)
            game_engine = GameEngine(game_name, game)
            if action["action"] == "connect":
                await game_engine.connect(username)
            elif action["action"] == "leave":
                await game_engine.leave(username)
            else:
                raise HTTPException(status_code=400, detail="Invalid action")
            logger.info(f"Sending game state to user {username}")
            await redis_client.set(f"game:{game_name}", json.dumps(game_engine.game))
            await websocket.send_json(game_engine.game)
    except WebSocketDisconnect:
        logger.info(f"Client {username} disconnected from game {game_name}")
    finally:
        # Perform any cleanup actions here
        logger.info(f"Connection to game {game_name} closed for user {username}")


app.include_router(router, prefix="/api/games", tags=["games"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
