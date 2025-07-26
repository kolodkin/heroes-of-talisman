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
    health: int
    level: int
    max_health: int
    skills: Dict[str, Any] = Field(default_factory=dict)
    dice: int
    attack: Optional[int] = None  # Only knight has attack


class PlayerModel(BaseModel):
    status: str = "connected"
    cards: list[str] = Field(default_factory=list)
    characters: Dict[str, CharacterModel] = Field(default_factory=dict)


class GameModel(BaseModel):
    stage: Optional[str] = None
    stage_meta: Optional[Dict[str, Any]] = None
    deck: list[str] = Field(default_factory=shuffled_deck)
    playing: Optional[str] = None
    selected_character: Optional[str] = None
    players: Dict[str, PlayerModel] = Field(default_factory=dict)


__DEFAULT_GAME__ = GameModel()


TraitDB = {
    "knight-1": {
        "max_health": 2,
        "skills": {},
        "dice": 1,
        "attack": 1,
    },
    "archer-1": {
        "max_health": 3,
        "skills": {},
        "dice": 1,
    },
    "mage-1": {
        "max_health": 2,
        "skills": {},
        "dice": 1,
    },
}
