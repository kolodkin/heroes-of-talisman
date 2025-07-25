import logging
import asyncio
import json
from http import HTTPStatus

from fastapi import APIRouter, FastAPI, WebSocket, HTTPException, WebSocketDisconnect

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
import uvicorn
from redis.asyncio import Redis

from .env import REDIS_HOST, REDIS_PORT
from .game_engine import __DEFAULT_GAME__, GameEngine, GameModel

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
redis_client = Redis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")


@app.get("/")
async def root():
    return PlainTextResponse("Welcome to 'Heroes of Talisman' game server!")


@app.get("/api/health")
async def health():
    return PlainTextResponse("Server is up")


class Game(BaseModel):
    name: str


@router.post("/")
async def add_game(new_game: Game):
    if len(new_game.name) == 0:
        raise HTTPException(status_code=400, detail="Game name cannot be empty")

    if await redis_client.exists(f"game:{new_game.name}"):
        raise HTTPException(status_code=400, detail="Game already exists")

    await redis_client.rpush("games", new_game.name)
    await redis_client.set(f"game:{new_game.name}", __DEFAULT_GAME__.model_dump_json())

    return {"message": "Game added successfully"}


@router.get("/")
async def get_games():
    games = await redis_client.lrange("games", 0, -1)
    return [game.decode("utf-8") for game in games]


@router.delete("/{gamename}")
async def delete_game(gamename: str):
    if not await redis_client.exists(f"game:{gamename}"):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")
    await redis_client.lrem("games", 0, gamename)
    await redis_client.delete(f"game:{gamename}")
    return {"message": "Game deleted successfully"}


@router.post("/{gamename}/reset")
async def reset_game(gamename: str):
    redis_meta = RedisMeta(gamename)

    if not await redis_client.exists(redis_meta.key):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")

    await redis_client.set(redis_meta.key, __DEFAULT_GAME__.model_dump_json())
    await redis_client.publish(redis_meta.channel, json.dumps(dict(event="game_update")))

    return {"message": "Game reset successfully"}


@app.post("/check-game-name")
async def check_game_name(game: Game):
    is_unique = not await redis_client.exists(f"game:{game.name}")
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


async def from_redis(redis: Redis, redis_meta: RedisMeta) -> "GameEngine":
    game = await redis.get(redis_meta.key)
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")

    game_model = GameModel.model_validate_json(game)
    if redis_meta.username is None:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="missing username")

    return GameEngine(redis_meta.gamename, redis_meta.username, game_model)


async def game_update_loop(websocket: WebSocket, redis_meta: RedisMeta):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(redis_meta.channel)
    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            if data["event"] == "game_update":
                game_engine = await from_redis(redis_client, redis_meta)
                await websocket.send_json(
                    {
                        "event": "game_update",
                        "game": game_engine.game.model_dump(),
                    }
                )
            else:
                logger.warning(f"Unknown event: {data}")


async def actions_loop(websocket: WebSocket, redis: Redis, redis_meta: RedisMeta):
    while True:
        action = await websocket.receive_text()
        action = json.loads(action)
        logger.info(f"Received action: {action}")

        success = False
        try:
            game_engine = await from_redis(redis, redis_meta)
            game_engine.action(action)
            success = True
        except Exception as e:
            logger.warning(f"Error processing action. action: {action}", exc_info=e)
            await websocket.send_json({"error": str(e), "class": e.__class__.__name__})

        if not success:
            continue

        logger.info(f"Sending game state to user '{game_engine.username}'")
        await redis_client.set(redis_meta.key, game_engine.dumps())
        await redis_client.publish(redis_meta.channel, json.dumps(dict(event="game_update")))


@app.websocket("/ws/{gamename}/{username}")
async def ws_game_endpoint(websocket: WebSocket, gamename: str, username: str):
    redis_meta = RedisMeta(gamename, username)

    await websocket.accept()

    if not await redis_client.exists(redis_meta.key):
        await websocket.send_json({"error": "Game not found"})
        await websocket.close()
        return

    logger.info(f"Connection to game {gamename} established for user {username}")
    try:
        await asyncio.gather(
            game_update_loop(websocket, redis_meta),
            actions_loop(websocket, redis_client, redis_meta),
        )
    except WebSocketDisconnect:
        game_engine = await from_redis(redis_client, redis_meta)
        game_engine.run_action("disconnect")
        await redis_client.set(redis_meta.key, game_engine.dumps())
        await redis_client.publish(redis_meta.channel, json.dumps(dict(event="game_update")))

        logger.info(f"Client '{username}' disconnected from game '{gamename}'")
    finally:
        # Perform any cleanup actions here
        logger.info(f"Connection to game '{gamename}' closed for user '{username}'")


app.include_router(router, prefix="/api/games", tags=["games"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
