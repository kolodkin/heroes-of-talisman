from typing import Dict

from .base import Action
from .connection import ConnectAction, LeaveAction, DisconnectAction
from .stage_character_select import CharacterPressAction, CharacterSelectAction

# Action mapping for dynamic action execution
ACTION_MAP: Dict[str, type[Action]] = {
    "connect": ConnectAction,
    "leave": LeaveAction,
    "disconnect": DisconnectAction,
    "character_press": CharacterPressAction,
    "character_select": CharacterSelectAction,
}
