from typing import Dict, Optional, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


CONNECTED = "connected"
DISCONNECTED = "disconnected"
CONNECTION_STATUS = Literal["connected", "disconnected"]

CHARACTER_SELECT = "character_select"
OPPONENT_SELECTION = "opponent_selection"
BATTLE_DICE_ROLL = "battle_dice_roll"
BATTLE_END = "battle_end"
STAGES_NAMES = Literal["character_select", "opponent_selection", "battle_dice_roll", "battle_end"]

KNIGHT = "knight"
ARCHER = "archer"
MAGE = "mage"
CHARACTER_TYPES = Literal["knight", "archer", "mage"]


class GameException(Exception):
    pass


class ReportedException(GameException):
    pass


def recursive_db_model_dump(model: BaseModel) -> dict:
    """
    Recursively dump model for database storage.
    Calls db_model_dump() on all nested StrictModel instances to exclude computed fields.
    """
    result = {}

    # Iterate over all fields and their values
    for field_name, field_value in model:
        if isinstance(field_value, BaseModel):
            # Nested model - call its db_model_dump if it's a StrictModel
            if hasattr(field_value, "db_model_dump"):
                result[field_name] = field_value.db_model_dump()
            else:
                result[field_name] = field_value.model_dump()
        elif isinstance(field_value, dict):
            # Dict of values (possibly models)
            result[field_name] = {
                k: (
                    v.db_model_dump()
                    if isinstance(v, BaseModel) and hasattr(v, "db_model_dump")
                    else v.model_dump() if isinstance(v, BaseModel) else v
                )
                for k, v in field_value.items()
            }
        elif isinstance(field_value, (list, tuple, set)):
            # Collection of values (possibly models) - preserve collection type
            processed_items = [
                (
                    item.db_model_dump()
                    if isinstance(item, BaseModel) and hasattr(item, "db_model_dump")
                    else item.model_dump() if isinstance(item, BaseModel) else item
                )
                for item in field_value
            ]
            # Preserve the original collection type
            result[field_name] = type(field_value)(processed_items)
        else:
            # Primitive value
            result[field_name] = field_value

    return result


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    def db_model_dump(self) -> dict:
        """Recursively use self.db_model_dump() on all nested models using recursive_model_dump()"""
        return recursive_db_model_dump(self)


class Card(StrictModel):
    face_up: bool = True
    selected: bool = False


class Deck(StrictModel):
    cards: list[Card] = Field(default_factory=list)
    visible: bool = True


class CharacterCard(StrictModel):
    level: int
    health: int
    max_health: int
    dice: int
    attack: int

    @computed_field
    @property
    def is_alive(self) -> bool:
        """Character is alive if health > 0"""
        return self.health > 0

    def db_model_dump(self) -> dict:
        return self.model_dump(exclude={"is_alive"})


class CharacterSelectMeta(StrictModel):
    """Stage metadata for character selection stage"""

    selected: str  # Currently highlighted character


class ActivePlayer1(StrictModel):
    """Selected character for battle"""

    player: str  # Character name


class ActivePlayer2(StrictModel):
    player: str
    character: str


class ActivePlayer3(StrictModel):
    player: str
    character: str
    dice_roll: list[int]


class ActivePlayer4(StrictModel):
    player: str
    character: str
    dice_roll: list[int]
    winner: bool


ActivePlayer = ActivePlayer1 | ActivePlayer2 | ActivePlayer3 | ActivePlayer4


class Opponent2(StrictModel):
    player: str
    character: str


class Opponent3(StrictModel):
    player: str
    character: str
    dice_roll: list[int]


class Opponent4(StrictModel):
    player: str
    character: str
    dice_roll: list[int]
    winner: bool


Opponent = Opponent2 | Opponent3 | Opponent4


class Player(StrictModel):
    name: str
    status: CONNECTION_STATUS = CONNECTED
    cards: list[str] = Field(default_factory=list)
    characters: Dict[CHARACTER_TYPES, CharacterCard] = Field(default_factory=dict)


class GamePlay(StrictModel):
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


DEFAULT_GAME = GamePlay()

KNIGHT_L1_DEFAULT_HEALTH = 2
KNIGHT_L1_MAX_HEALTH = 2
KNIGHT_L1_DICE = 1
KNIGHT_L1_ATTACK = 1

ARCHER_L1_DEFAULT_HEALTH = 3
ARCHER_L1_MAX_HEALTH = 3
ARCHER_L1_DICE = 1
ARCHER_L1_ATTACK = 0

MAGE_L1_DEFAULT_HEALTH = 2
MAGE_L1_MAX_HEALTH = 2
MAGE_L1_DICE = 1
MAGE_L1_ATTACK = 0

CHARACTER_DEFAULT_STATS = {
    "knight": {
        "health": KNIGHT_L1_DEFAULT_HEALTH,
        "max_health": KNIGHT_L1_MAX_HEALTH,
        "dice": KNIGHT_L1_DICE,
        "attack": KNIGHT_L1_ATTACK,
    },
    "archer": {
        "health": ARCHER_L1_DEFAULT_HEALTH,
        "max_health": ARCHER_L1_MAX_HEALTH,
        "dice": ARCHER_L1_DICE,
        "attack": ARCHER_L1_ATTACK,
    },
    "mage": {
        "health": MAGE_L1_DEFAULT_HEALTH,
        "max_health": MAGE_L1_MAX_HEALTH,
        "dice": MAGE_L1_DICE,
        "attack": MAGE_L1_ATTACK,
    },
}


def init_characters(level: int = 1) -> Dict[CHARACTER_TYPES, CharacterCard]:
    """Initialize all character types with default stats"""
    return {
        char_type: CharacterCard(level=level, **CHARACTER_DEFAULT_STATS[char_type])
        for char_type in [KNIGHT, ARCHER, MAGE]
    }
