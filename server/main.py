from fastapi import APIRouter, FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
import uvicorn
from redis.asyncio import Redis

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
    await redis_client.set(f"game:{game.name}", 1)

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


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Process the received data and update the game state in Redis
        # await redis_client.set(game_id, data)
        # Broadcast the updated game state to all connected clients
        await websocket.send_text(data)


app.include_router(router, prefix="/api/games", tags=["games"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
