from typing import Dict, Optional, Literal

from pydantic import BaseModel, Field


CONNECTED = "connected"
DISCONNECTED = "disconnected"
CONNECTION_STATUS = Literal["connected", "disconnected"]


class GameException(Exception):
    pass


class ReportedException(GameException):
    pass


class Card(BaseModel):
    face_up: bool = True
    selected: bool = False


class Deck(BaseModel):
    cards: list[Card] = Field(default_factory=list)
    visible: bool = True


class CharacterCard(BaseModel):
    level: int
    health: int
    max_health: int
    dice: int
    attack: Optional[int] = None  # Only knight has attack


class Player(BaseModel):
    name: str
    status: CONNECTION_STATUS = CONNECTED
    cards: list[str] = Field(default_factory=list)
    characters: Dict[str, CharacterCard] = Field(default_factory=dict)


class GameBoard(BaseModel):
    stage: str = "start"
    playing: Optional[str] = None  # the player who is currently playing
    players: dict[str, Player] = Field(default_factory=dict)

    def reorder_players(self, username: str) -> dict[str, Player]:
        """Return players dict with username first (circular shift)"""
        if username not in self.players:
            return self.players

        # Get all player keys
        player_keys = list(self.players.keys())

        # Find the index of the username
        user_index = player_keys.index(username)

        # Circular shift: username first, then the rest
        reordered_keys = player_keys[user_index:] + player_keys[:user_index]

        # Build new dict with reordered keys
        return {key: self.players[key] for key in reordered_keys}


__DEFAULT_GAME__ = GameBoard()


CHARACTER_DEFAULT_STATS = {
    "knight": {
        "health": 2,
        "max_health": 2,
        "dice": 1,
        "attack": 1,
    },
    "archer": {
        "health": 2,
        "max_health": 3,
        "dice": 1,
    },
    "mage": {
        "health": 2,
        "max_health": 2,
        "dice": 1,
    },
}
