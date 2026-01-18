"""
Base models and utilities - foundation for effects, abilities, and gameplay modules.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


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

########################################################
# Effect names
########################################################
ATTACK_BONUS = "attack_bonus"
ATTACK_NEG_BONUS = "attack_neg_bonus"
REROLL_DICE = "reroll_dice"
SKIP_TURN = "skip_turn"
DRAW_CARD = "draw_card"

########################################################
# Effect apply_to targets
########################################################
APPLY_TO_SELF = "self"  # Applied to active player's character when ability is selected
APPLY_TO_BATTLE_OPPONENT = "battle_opponent"  # Applied to opponent when battle starts
APPLY_TO_SELECTED_OPPONENT = "selected_opponent"  # Requires ability_opponent_selection stage

APPLY_TO_TARGETS = [APPLY_TO_SELF, APPLY_TO_BATTLE_OPPONENT, APPLY_TO_SELECTED_OPPONENT]
ApplyToTarget = Literal[*APPLY_TO_TARGETS]

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


########################################################
# Exceptions
########################################################
class GameException(Exception):
    pass


class ReportedException(GameException):
    pass


########################################################
# Base model utilities
########################################################
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


########################################################
# Re-exports for backwards compatibility
########################################################
# Re-export from abilities
from .abilities import (
    Ability,
    ABILITIES_MAP,
    AbilityName,
    ABILITIES_NAMES,
    BATTLE_HOWL,
    BOUNCING_ARROW,
    FREEZE,
    EFFECTS_SOURCE_ABILITY_MAP,
)

# Re-export from effects
from .effects import (
    Effect,
    SkipTurnEffect,
    AttackBonusEffect,
    RerollDiceEffect,
    AttackNegBonusEffect,
    DrawCardEffect,
    EffectUnion,
    EffectTotal,
)

# Re-export from gameplay
from .gameplay import (
    Character,
    CharacterSelectMeta,
    AbilitySelectMeta,
    ActivePlayer1,
    BattleResult,
    ActivePlayer2,
    ActivePlayer3,
    ActivePlayer4,
    ActivePlayer,
    Opponent2,
    Opponent3,
    Opponent4,
    Opponent,
    Player,
    GamePlay,
    DEFAULT_GAME,
    KNIGHT_L1_DEFAULT_HEALTH,
    KNIGHT_L1_MAX_HEALTH,
    KNIGHT_L1_DICE,
    KNIGHT_L1_ATTACK,
    KNIGHT_L1_ABILITY,
    ARCHER_L1_DEFAULT_HEALTH,
    ARCHER_L1_MAX_HEALTH,
    ARCHER_L1_DICE,
    ARCHER_L1_ATTACK,
    ARCHER_L1_ABILITY,
    MAGE_L1_DEFAULT_HEALTH,
    MAGE_L1_MAX_HEALTH,
    MAGE_L1_DICE,
    MAGE_L1_ATTACK,
    MAGE_L1_ABILITY,
    CHARACTER_DEFAULT_STATS,
    init_characters,
)
