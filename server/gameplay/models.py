from typing import Dict, Optional, Literal

from pydantic import BaseModel, Field


CONNECTED = "connected"
DISCONNECTED = "disconnected"
CONNECTION_STATUS = Literal["connected", "disconnected"]

CHARACTER_SELECT = "character_select"
OPPONENT_SELECTION = "opponent_selection"
BATTLE = "battle"
STAGES_NAMES = Literal["character_select", "opponent_selection", "battle"]

KNIGHT = "knight"
ARCHER = "archer"
MAGE = "mage"
CHARACTER_TYPES = Literal["knight", "archer", "mage"]


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


class CharacterSelectMeta(BaseModel):
    """Stage metadata for character selection stage"""

    selected: str  # Currently highlighted character


class ActivePlayer1(BaseModel):
    """Selected character for battle"""

    player: str  # Character name


class ActivePlayer2(BaseModel):
    player: str
    character: str


class ActivePlayer3(BaseModel):
    player: str
    character: str
    dice_roll: list[int]


class ActivePlayer4(BaseModel):
    player: str
    character: str
    dice_roll: list[int]
    winner: bool


ActivePlayer = ActivePlayer1 | ActivePlayer2 | ActivePlayer3 | ActivePlayer4


class Opponent2(BaseModel):
    player: str
    character: str


class Opponent3(BaseModel):
    player: str
    character: str
    dice_roll: list[int]


class Opponent4(BaseModel):
    player: str
    character: str
    dice_roll: list[int]
    winner: bool


Opponent = Opponent2 | Opponent3 | Opponent4


class Player(BaseModel):
    name: str
    status: CONNECTION_STATUS = CONNECTED
    cards: list[str] = Field(default_factory=list)
    characters: Dict[str, CharacterCard] = Field(default_factory=dict)


class GamePlay(BaseModel):
    stage: STAGES_NAMES = CHARACTER_SELECT
    active: Optional[ActivePlayer] = None  # The active player and its selections
    players: dict[str, Player] = Field(default_factory=dict)
    opponent: Optional[Opponent] = None  # Selected opponent for battle
    stage_meta: Optional[CharacterSelectMeta | Opponent2] = None  # Temporary stage-specific metadata

    def reorder_players(self, username: str):
        """Reorder players dict in-place with username first (circular shift)"""
        if username not in self.players:
            return

        # Get all player keys
        player_keys = list(self.players.keys())

        # Find the index of the username
        user_index = player_keys.index(username)

        # Circular shift: username first, then the rest
        reordered_keys = player_keys[user_index:] + player_keys[:user_index]

        # Build new dict with reordered keys
        reordered_dict = {key: self.players[key] for key in reordered_keys}

        # Update in-place
        self.players.clear()
        self.players.update(reordered_dict)


__DEFAULT_GAME__ = GamePlay()


CHARACTER_DEFAULT_STATS = {
    "knight": {
        "health": 2,
        "max_health": 2,
        "dice": 1,
        "attack": 1,
    },
    "archer": {
        "health": 3,
        "max_health": 3,
        "dice": 1,
    },
    "mage": {
        "health": 2,
        "max_health": 2,
        "dice": 1,
    },
}
