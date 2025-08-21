import random
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class GameException(Exception):
    pass


class ReportedException(GameException):
    pass


__MAX_PLAYERS__ = 4

__DECK__ = ["talisman", "golden_apple"]


def shuffled_deck():
    deck = __DECK__.copy()
    random.shuffle(deck)
    return deck


class CharacterModel(BaseModel):
    level: int
    health: int
    max_health: int
    dice: int
    attack: Optional[int] = None  # Only knight has attack


class PlayerModel(BaseModel):
    name: str
    status: str = "connected"
    cards: list[str] = Field(default_factory=list)
    characters: Dict[str, CharacterModel] = Field(default_factory=dict)


class GameModel(BaseModel):
    stage: str = "start"
    playing: Optional[str] = None  # the player who is currently playing
    players: list[PlayerModel] = Field(default_factory=list)


__DEFAULT_GAME__ = GameModel()


CHARACTER_DEFAULT_STATS = {
    "knight-1": {
        "health": 2,
        "max_health": 2,
        "dice": 1,
        "attack": 1,
    },
    "archer-1": {
        "health": 2,
        "max_health": 3,
        "dice": 1,
    },
    "mage-1": {
        "health": 2,
        "max_health": 2,
        "dice": 1,
    },
}
