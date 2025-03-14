from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
import uvicorn

# import aioredis

app = FastAPI()

# Initialize Redis client
# redis_client = aioredis.from_url("redis://localhost")


@app.get("/")
async def read_root():
    return PlainTextResponse("Welcome to 'Heroes of Talisman' game server!")


@app.get("/health")
async def read_root():
    return PlainTextResponse("Server is up")


@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Process the received data and update the game state in Redis
        # await redis_client.set(game_id, data)
        # Broadcast the updated game state to all connected clients
        await websocket.send_text(data)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
