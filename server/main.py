from fastapi import FastAPI

from .routers import auth, api, websocket_router


app = FastAPI(
    title="Heroes of Talisman Game Engine",
    description="Turn-based card game platform with real-time multiplayer",
    version="0.1.0"
)

# Include routers
app.include_router(api.router)
app.include_router(auth.router)
app.include_router(websocket_router.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 