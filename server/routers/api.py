from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/api", tags=["api"])


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
            "health": "/api/health"
        }
    } 