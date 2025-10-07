from typing import Dict

from .action import Action
from .connection import ConnectAction, LeaveAction, DisconnectAction
from .stage_character_select import CharacterPressAction, CharacterSelectAction
from .stage_opponent_selection import OpponentPressAction, OpponentSelectAction
from .stage_battle import ActivePlayerRollAction, OpponentRollAction
from .battle_end import BattleEndAction

# Action mapping for dynamic action execution
ACTION_MAP: Dict[str, type[Action]] = {
    "connect": ConnectAction,
    "leave": LeaveAction,
    "disconnect": DisconnectAction,
    "character_press": CharacterPressAction,
    "character_select": CharacterSelectAction,
    "opponent_press": OpponentPressAction,
    "opponent_select": OpponentSelectAction,
    "active_player_roll": ActivePlayerRollAction,
    "opponent_roll": OpponentRollAction,
    "battle_end": BattleEndAction,
}
