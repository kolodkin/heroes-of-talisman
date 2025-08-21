from typing import Dict

from .base import Action
from .connection import ConnectAction, LeaveAction, DisconnectAction

# Action mapping for dynamic action execution
ACTION_MAP: Dict[str, type[Action]] = {
    "connect": ConnectAction,
    "leave": LeaveAction,
    "disconnect": DisconnectAction,
}
