from fastapi import APIRouter, WebSocket, Query

router = APIRouter()


# @router.websocket("/ws/game/{game_id}/{user_id}")
# async def websocket_game_endpoint(
#     websocket: WebSocket,
#     game_id: str,
#     user_id: str,
#     token: str = Query(..., description="JWT authentication token")
# ):
#     """WebSocket endpoint for game connections with JWT authentication.
    
#     Args:
#         websocket: WebSocket connection
#         game_id: Game identifier
#         user_id: User identifier
#         token: JWT authentication token passed as query parameter
#     """
#     await websocket_endpoint(websocket, game_id, user_id, token) 