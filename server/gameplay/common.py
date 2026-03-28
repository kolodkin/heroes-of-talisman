"""
Base models and utilities - foundation for effects, abilities, and gameplay modules.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

# Re-export action names for backwards compatibility
from .actions_names import (
    ACTION_CONNECT,
    ACTION_LEAVE,
    ACTION_DISCONNECT,
    ACTION_CHARACTER_PRESS,
    ACTION_CHARACTER_SELECT,
    ACTION_CARD_DRAW,
    ACTION_CARD_SELECT,
    ACTION_ABILITY_PRESS,
    ACTION_ABILITY_SELECT,
    ACTION_ABILITY_OPPONENT_PRESS,
    ACTION_ABILITY_OPPONENT_SELECT,
    ACTION_ABILITY_ITEM_PRESS,
    ACTION_ABILITY_ITEM_SELECT,
    ACTION_OPPONENT_PRESS,
    ACTION_OPPONENT_SELECT,
    ACTION_ACTIVE_PLAYER_ROLL,
    ACTION_OPPONENT_ROLL,
    ACTION_REROLL,
    ACTION_REROLL_EFFECT,
    ACTION_BATTLE_END,
    ACTION_SKIP_TURN,
    ACTION_DEBUG_SET_BATTLE_DICE_ROLLS,
    ACTION_DEBUG_SET_DRAWN_CARD,
    ACTION_NAMES,
    ActionName,
)


########################################################
# Connection statuses
########################################################
STATUS_CONNECTED = "connected"
STATUS_DISCONNECTED = "disconnected"
CONNECTION_STATUSES = [STATUS_CONNECTED, STATUS_DISCONNECTED]
ConnectionStatus = Literal[*CONNECTION_STATUSES]

########################################################
# Character types
########################################################
CHARACTER_KNIGHT = "knight"
CHARACTER_ARCHER = "archer"
CHARACTER_MAGE = "mage"
CHARACTER_TYPES = [CHARACTER_KNIGHT, CHARACTER_ARCHER, CHARACTER_MAGE]
ChatacterType = Literal[*CHARACTER_TYPES]

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
