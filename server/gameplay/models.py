from typing import Dict, Optional, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


CONNECTED = "connected"
DISCONNECTED = "disconnected"
CONNECTION_STATUSES = [CONNECTED, DISCONNECTED]
ConnectionStatus = Literal[*CONNECTION_STATUSES]

CHARACTER_SELECT = "character_select"
ABILITY_SELECTION = "ability_selection"
ABILITY_OPPONENT_SELECTION = "ability_opponent_selection"
OPPONENT_SELECTION = "opponent_selection"
BATTLE_DICE_ROLL = "battle_dice_roll"
BATTLE_END = "battle_end"
STAGES_NAMES = [CHARACTER_SELECT, ABILITY_SELECTION, ABILITY_OPPONENT_SELECTION, OPPONENT_SELECTION, BATTLE_DICE_ROLL, BATTLE_END]
StageName = Literal[*STAGES_NAMES]

KNIGHT = "knight"
ARCHER = "archer"
MAGE = "mage"
CHARACTER_TYPES = [KNIGHT, ARCHER, MAGE]
ChatacterType = Literal[*CHARACTER_TYPES]

BATTLE_HOWL = "battle_howl"
BOUNCING_ARROW = "bouncing_arrow"
FREEZE = "freeze"
ABILITIES_NAMES: list[str] = [BATTLE_HOWL, BOUNCING_ARROW, FREEZE]
AbilityName = Literal[*ABILITIES_NAMES]

# Action names
CONNECT = "connect"
LEAVE = "leave"
DISCONNECT = "disconnect"
CHARACTER_PRESS = "character_press"
CHARACTER_SELECT_ACTION = "character_select"
ABILITY_PRESS = "ability_press"
ABILITY_SELECT = "ability_select"
OPPONENT_PRESS = "opponent_press"
OPPONENT_SELECT = "opponent_select"
ACTIVE_PLAYER_ROLL = "active_player_roll"
OPPONENT_ROLL = "opponent_roll"
ACTION_REROLL = "action_reroll"
BATTLE_END_ACTION = "battle_end"
DEBUG_SET_BATTLE_DICE_ROLLS = "debug_set_battle_dice_rolls"

ACTION_NAMES = [
    CONNECT,
    LEAVE,
    DISCONNECT,
    CHARACTER_PRESS,
    CHARACTER_SELECT_ACTION,
    ABILITY_PRESS,
    ABILITY_SELECT,
    OPPONENT_PRESS,
    OPPONENT_SELECT,
    ACTIVE_PLAYER_ROLL,
    OPPONENT_ROLL,
    ACTION_REROLL,
    BATTLE_END_ACTION,
    DEBUG_SET_BATTLE_DICE_ROLLS,
]
ActionName = Literal[*ACTION_NAMES]


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


class Effect(StrictModel):
    """
    Base class for all effects.
    """

    source: AbilityName
    # at the end of this action, the effect is disposed (removed from the character effects list)
    dispose_action: ActionName  # Action name in which the effect should be disposed, sometimes with custom conditions.


class SkipTurnEffect(Effect):
    """
    Charachter can't participate in the next turn.
    """

    dispose_action: ActionName = BATTLE_END_ACTION
    skip_next_turn: bool = True


class AttackBonusEffect(Effect):
    """
    Character's attack is increased by the value of the effect.
    """

    dispose_action: ActionName = BATTLE_END_ACTION
    attack_bonus: int


class RerollDiceEffect(Effect):
    """
    Character's dice are rerolled if lost the battle.
    At the end of the battle, the effect is disposed if the character lost the battle
    causes the BATTLE_END_ACTION action to invoke RerollAction (reroll the dice).
    """

    dispose_action: ActionName = BATTLE_END_ACTION
    reroll_dice: bool = True


class AttackNegBonusEffect(Effect):
    """
    Character's attack is decreased by the value of the effect.
    """

    dispose_action: ActionName = BATTLE_END_ACTION
    attack_neg_bonus: int


class Ability(StrictModel):
    name: str
    description: str
    effects: list[Effect] = Field(default_factory=list)  # effects that are applied when the ability is used


ABILITIES_MAP: dict[AbilityName, Ability] = {
    BATTLE_HOWL: Ability(
        name=BATTLE_HOWL,
        description="Battle Howl",
        effects=[
            AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-2),
        ],
    ),
    BOUNCING_ARROW: Ability(
        name=BOUNCING_ARROW,
        description="Bouncing Arrow",
        effects=[
            RerollDiceEffect(source=BOUNCING_ARROW),
        ],
    ),
    FREEZE: Ability(
        name=FREEZE,
        description="Freeze",
        effects=[
            SkipTurnEffect(source=FREEZE),
        ],
    ),
}


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
    abilities: list[Ability] = Field(default_factory=list)
    effects: list[Effect] = Field(default_factory=list)

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


class BattleResult(StrictModel):
    winner: bool
    score: int  # result of the battle, sum of dice_roll and attack


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
    result: BattleResult


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
    result: BattleResult


Opponent = Opponent2 | Opponent3 | Opponent4


class Player(StrictModel):
    name: str
    status: ConnectionStatus = CONNECTED
    cards: list[str] = Field(default_factory=list)
    characters: Dict[ChatacterType, CharacterCard] = Field(default_factory=dict)


class GamePlay(StrictModel):
    stage: StageName = CHARACTER_SELECT
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
KNIGHT_L1_ABILITY = BATTLE_HOWL

ARCHER_L1_DEFAULT_HEALTH = 3
ARCHER_L1_MAX_HEALTH = 3
ARCHER_L1_DICE = 1
ARCHER_L1_ATTACK = 0
ARCHER_L1_ABILITY = BOUNCING_ARROW

MAGE_L1_DEFAULT_HEALTH = 2
MAGE_L1_MAX_HEALTH = 2
MAGE_L1_DICE = 1
MAGE_L1_ATTACK = 0
MAGE_L1_ABILITY = FREEZE

CHARACTER_DEFAULT_STATS = {
    "knight": {
        "health": KNIGHT_L1_DEFAULT_HEALTH,
        "max_health": KNIGHT_L1_MAX_HEALTH,
        "dice": KNIGHT_L1_DICE,
        "attack": KNIGHT_L1_ATTACK,
        "abilities": [ABILITIES_MAP[KNIGHT_L1_ABILITY]],
    },
    "archer": {
        "health": ARCHER_L1_DEFAULT_HEALTH,
        "max_health": ARCHER_L1_MAX_HEALTH,
        "dice": ARCHER_L1_DICE,
        "attack": ARCHER_L1_ATTACK,
        "abilities": [ABILITIES_MAP[ARCHER_L1_ABILITY]],
    },
    "mage": {
        "health": MAGE_L1_DEFAULT_HEALTH,
        "max_health": MAGE_L1_MAX_HEALTH,
        "dice": MAGE_L1_DICE,
        "attack": MAGE_L1_ATTACK,
        "abilities": [ABILITIES_MAP[MAGE_L1_ABILITY]],
    },
}


def init_characters(level: int = 1) -> Dict[ChatacterType, CharacterCard]:
    """Initialize all character types with default stats"""
    return {
        char_type: CharacterCard(level=level, **CHARACTER_DEFAULT_STATS[char_type])
        for char_type in [KNIGHT, ARCHER, MAGE]
    }
