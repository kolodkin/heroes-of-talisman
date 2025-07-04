from typing import List, Optional
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel


router = APIRouter(prefix="/api", tags=["api"])


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
            "websocket": "/ws/game/{game_id}/{user_id}?token=<jwt_token>",
        },
    }
