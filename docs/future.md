# Future Improvements

## Game Deleted Indication

When a game is deleted while players are connected, the server sends a generic "Game not found" error. The client handles this by showing an error toast and redirecting to the home page, but the message is unclear — it doesn't distinguish between a game that never existed and one that was actively deleted.

**Improvement:** Send a distinct `"Game deleted"` event so the client can show a specific message like "This game has been deleted" instead of "Game not found".
