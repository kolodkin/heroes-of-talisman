from typing import Dict

from .action import Action
from .connection import ConnectAction, LeaveAction, DisconnectAction
from .stage_character_select import CharacterPressAction, CharacterSelectAction
from .stage_opponent_selection import OpponentPressAction, OpponentSelectAction

# Action mapping for dynamic action execution
ACTION_MAP: Dict[str, type[Action]] = {
    "connect": ConnectAction,
    "leave": LeaveAction,
    "disconnect": DisconnectAction,
    "character_press": CharacterPressAction,
    "character_select": CharacterSelectAction,
    "opponent_press": OpponentPressAction,
    "opponent_select": OpponentSelectAction,
}
