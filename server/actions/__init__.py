from typing import Dict

from .base import Action
from .character import CharacterSelectAction, CharacterSelectedAction
from .card import CardDrawAction, CardSelectAction
from .connection import ConnectAction, LeaveAction, DisconnectAction

# Action mapping for dynamic action execution
ACTION_MAP: Dict[str, type[Action]] = {
    "character_select": CharacterSelectAction,
    "character_selected": CharacterSelectedAction,
    "card_draw": CardDrawAction,
    "card_select": CardSelectAction,
    "connect": ConnectAction,
    "leave": LeaveAction,
    "disconnect": DisconnectAction,
}
