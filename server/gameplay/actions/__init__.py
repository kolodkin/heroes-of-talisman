from typing import Dict

from ..common import (
    CONNECT,
    LEAVE,
    DISCONNECT,
    CHARACTER_PRESS,
    CHARACTER_SELECT_ACTION,
    CARD_DRAW_ACTION,
    CARD_SELECT_ACTION,
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
)  # Action constants stay in models.py
from .action import Action
from .connection import ConnectAction, LeaveAction, DisconnectAction
from .stage_character_select import CharacterPressAction, CharacterSelectAction
from .stage_card_draw import CardDrawAction, CardSelectAction
from .stage_ability_selection import AbilityPressAction, AbilitySelectAction
from .stage_ability_opponent_selection import AbilityOpponentPressAction, AbilityOpponentSelectAction
from .stage_opponent_selection import OpponentPressAction, OpponentSelectAction
from .stage_battle import ActivePlayerRollAction, OpponentRollAction, RerollAction, RerollEffectAction, DebugSetBattleDiceRollsAction
from .battle_end import BattleEndAction

# Action mapping for dynamic action execution
ACTION_MAP: Dict[str, type[Action]] = {
    CONNECT: ConnectAction,
    LEAVE: LeaveAction,
    DISCONNECT: DisconnectAction,
    CHARACTER_PRESS: CharacterPressAction,
    CHARACTER_SELECT_ACTION: CharacterSelectAction,
    CARD_DRAW_ACTION: CardDrawAction,
    CARD_SELECT_ACTION: CardSelectAction,
    ABILITY_PRESS: AbilityPressAction,
    ABILITY_SELECT: AbilitySelectAction,
    ABILITY_OPPONENT_PRESS: AbilityOpponentPressAction,
    ABILITY_OPPONENT_SELECT: AbilityOpponentSelectAction,
    OPPONENT_PRESS: OpponentPressAction,
    OPPONENT_SELECT: OpponentSelectAction,
    ACTIVE_PLAYER_ROLL: ActivePlayerRollAction,
    OPPONENT_ROLL: OpponentRollAction,
    ACTION_REROLL: RerollAction,
    ACTION_REROLL_EFFECT: RerollEffectAction,
    BATTLE_END_ACTION: BattleEndAction,
    DEBUG_SET_BATTLE_DICE_ROLLS: DebugSetBattleDiceRollsAction,
}
