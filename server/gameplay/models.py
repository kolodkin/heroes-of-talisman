from typing import Dict, Optional

from pydantic import BaseModel, Field


class GameException(Exception):
    pass


class ReportedException(GameException):
    pass


class CardModel(BaseModel):
    face_up: bool = True
    selected: bool = False


class DeckModel(BaseModel):
    cards: list[CardModel] = Field(default_factory=list)
    visible: bool = True


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


class GameBoard(BaseModel):
    stage: str = "start"
    playing: str = None  # the player who is currently playing
    players: dict[str, PlayerModel] = Field(default_factory=dict)


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
