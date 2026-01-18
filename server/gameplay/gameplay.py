from __future__ import annotations

from typing import Dict, Optional, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

########################################################
# Connection statuses
########################################################
CONNECTED = "connected"
DISCONNECTED = "disconnected"
CONNECTION_STATUSES = [CONNECTED, DISCONNECTED]
ConnectionStatus = Literal[*CONNECTION_STATUSES]

########################################################
# Stages
########################################################
CHARACTER_SELECT = "character_select"
ABILITY_SELECTION = "ability_selection"
ABILITY_OPPONENT_SELECTION = "ability_opponent_selection"
OPPONENT_SELECTION = "opponent_selection"
BATTLE_DICE_ROLL = "battle_dice_roll"
BATTLE_END = "battle_end"
STAGES_NAMES = [
    CHARACTER_SELECT,
    ABILITY_SELECTION,
    ABILITY_OPPONENT_SELECTION,
    OPPONENT_SELECTION,
    BATTLE_DICE_ROLL,
    BATTLE_END,
]
StageName = Literal[*STAGES_NAMES]

########################################################
# Character types
########################################################
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

# Effect names
ATTACK_BONUS = "attack_bonus"
ATTACK_NEG_BONUS = "attack_neg_bonus"
REROLL_DICE = "reroll_dice"
SKIP_TURN = "skip_turn"
DRAW_CARD = "draw_card"

# Effect apply_to targets - specifies who receives the effect
APPLY_TO_SELF = "self"  # Applied to active player's character when ability is selected
APPLY_TO_BATTLE_OPPONENT = "battle_opponent"  # Applied to opponent when battle starts
APPLY_TO_SELECTED_OPPONENT = "selected_opponent"  # Requires ability_opponent_selection stage

APPLY_TO_TARGETS = [APPLY_TO_SELF, APPLY_TO_BATTLE_OPPONENT, APPLY_TO_SELECTED_OPPONENT]
ApplyToTarget = Literal[*APPLY_TO_TARGETS]

# Effect-to-Source mapping: defines which abilities can create which effects
# This is used for validation to ensure effects have valid source abilities
EFFECTS_SOURCE_ABILITY_MAP: dict[str, set[str]] = {
    ATTACK_BONUS: {BATTLE_HOWL},  # AttackBonusEffect can come from BATTLE_HOWL
    ATTACK_NEG_BONUS: set(),  # AttackNegBonusEffect - TBD: add abilities that grant attack penalty
    REROLL_DICE: {BOUNCING_ARROW},  # RerollDiceEffect can come from BOUNCING_ARROW
    SKIP_TURN: {FREEZE},  # SkipTurnEffect can come from FREEZE
    DRAW_CARD: set(),  # DrawCardEffect - TBD: add abilities that grant card draw
}

########################################################
# Actions
########################################################
CONNECT = "connect"
LEAVE = "leave"
DISCONNECT = "disconnect"
CHARACTER_PRESS = "character_press"
CHARACTER_SELECT_ACTION = "character_select"
ABILITY_PRESS = "ability_press"
ABILITY_SELECT = "ability_select"
ABILITY_OPPONENT_PRESS = "ability_opponent_press"
ABILITY_OPPONENT_SELECT = "ability_opponent_select"
OPPONENT_PRESS = "opponent_press"
OPPONENT_SELECT = "opponent_select"
ACTIVE_PLAYER_ROLL = "active_player_roll"
OPPONENT_ROLL = "opponent_roll"
ACTION_REROLL = "action_reroll"
ACTION_REROLL_EFFECT = "action_reroll_effect"
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
    ABILITY_OPPONENT_PRESS,
    ABILITY_OPPONENT_SELECT,
    OPPONENT_PRESS,
    OPPONENT_SELECT,
    ACTIVE_PLAYER_ROLL,
    OPPONENT_ROLL,
    ACTION_REROLL,
    ACTION_REROLL_EFFECT,
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


class Character(StrictModel):

    level: int
    health: int
    max_health: int
    dice: int
    attack: int
    abilities: list[Ability] = Field(default_factory=list)
    effects: list[EffectUnion] = Field(default_factory=list)

    @computed_field
    @property
    def is_alive(self) -> bool:
        """Character is alive if health > 0"""
        return self.health > 0

    @computed_field
    @property
    def effect(self) -> EffectTotal:
        """Aggregate all active effects into a single EffectTotal"""
        from .effects import (
            EffectTotal,
            AttackBonusEffect,
            AttackNegBonusEffect,
            SkipTurnEffect,
            RerollDiceEffect,
            DrawCardEffect,
        )

        total = EffectTotal()

        for eff in self.effects:
            if isinstance(eff, AttackBonusEffect):
                total.attack_bonus += eff.attack_bonus
            elif isinstance(eff, AttackNegBonusEffect):
                total.attack_neg_bonus += eff.attack_neg_bonus
            elif isinstance(eff, SkipTurnEffect):
                total.skip_next_turn = total.skip_next_turn or eff.skip_next_turn
            elif isinstance(eff, RerollDiceEffect):
                total.reroll_dice_available = True
            elif isinstance(eff, DrawCardEffect):
                total.draw_card_count += eff.draw_count

        return total

    def db_model_dump(self) -> dict:
        return self.model_dump(exclude={"is_alive", "effect"})


class CharacterSelectMeta(StrictModel):
    """Stage metadata for character selection stage"""

    selected: str  # Currently highlighted character


class AbilitySelectMeta(StrictModel):
    """Stage metadata for ability selection stage"""

    selected: str  # Currently highlighted ability


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
    characters: Dict[ChatacterType, Character] = Field(default_factory=dict)


########################################################
# GamePlay model
########################################################
class GamePlay(StrictModel):
    stage: StageName = CHARACTER_SELECT
    players: dict[str, Player] = Field(default_factory=dict)
    active: Optional[ActivePlayer] = None  # The active player and its selections
    ability: Optional[Ability] = None  # Selected ability
    ability_opponent: Optional[Opponent2] = None  # Selected ability opponent
    opponent: Optional[Opponent] = None  # Selected opponent for battle
    stage_meta: Optional[Ability | CharacterSelectMeta | AbilitySelectMeta | Opponent2] = None  # Temporary stage-specific metadata

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

def get_character_default_stats() -> dict:
    """Get character default stats with abilities. Uses lazy import to avoid circular dependency."""
    from .abilities import ABILITIES_MAP

    return {
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


# Lazy-evaluated CHARACTER_DEFAULT_STATS for backwards compatibility
_CHARACTER_DEFAULT_STATS = None


def _get_cached_character_default_stats():
    global _CHARACTER_DEFAULT_STATS
    if _CHARACTER_DEFAULT_STATS is None:
        _CHARACTER_DEFAULT_STATS = get_character_default_stats()
    return _CHARACTER_DEFAULT_STATS


# Property-like access for CHARACTER_DEFAULT_STATS
class _CharacterDefaultStatsProxy:
    def __getitem__(self, key):
        return _get_cached_character_default_stats()[key]

    def __iter__(self):
        return iter(_get_cached_character_default_stats())

    def items(self):
        return _get_cached_character_default_stats().items()

    def keys(self):
        return _get_cached_character_default_stats().keys()

    def values(self):
        return _get_cached_character_default_stats().values()


CHARACTER_DEFAULT_STATS = _CharacterDefaultStatsProxy()


def init_characters(level: int = 1) -> Dict[ChatacterType, Character]:
    """Initialize all character types with default stats"""
    stats = get_character_default_stats()
    return {
        char_type: Character(level=level, **stats[char_type])
        for char_type in [KNIGHT, ARCHER, MAGE]
    }
