from pydantic import BaseModel, Field


class CardModel(BaseModel):
    face_up: bool = True
    selected: bool = False


class DeckModel(BaseModel):
    cards: list[CardModel] = Field(default_factory=list)
    visible: bool = True


class GameBoard(BaseModel):
    stage: str = "start"
    playing: [str] = None  # the player who is currently playing
    players: dict[str, PlayerModel] = Field(default_factory=dict)
