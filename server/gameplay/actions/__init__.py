from typing import Dict

from ..common import (
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
)  # Action constants stay in models.py
from .action import Action
from .connection import ConnectAction, LeaveAction, DisconnectAction
from .stage_character_select import CharacterPressAction, CharacterSelectAction, SkipTurnAction
from .stage_card_draw import CardDrawAction, CardSelectAction, DebugSetDrawnCardAction
from .stage_ability_selection import AbilityPressAction, AbilitySelectAction
from .stage_ability_opponent_selection import AbilityOpponentPressAction, AbilityOpponentSelectAction
from .stage_opponent_selection import OpponentPressAction, OpponentSelectAction
from .stage_battle import ActivePlayerRollAction, OpponentRollAction, RerollAction, RerollEffectAction, DebugSetBattleDiceRollsAction
from .battle_end import BattleEndAction

# Action mapping for dynamic action execution
ACTION_MAP: Dict[str, type[Action]] = {
    ACTION_CONNECT: ConnectAction,
    ACTION_LEAVE: LeaveAction,
    ACTION_DISCONNECT: DisconnectAction,
    ACTION_CHARACTER_PRESS: CharacterPressAction,
    ACTION_CHARACTER_SELECT: CharacterSelectAction,
    ACTION_CARD_DRAW: CardDrawAction,
    ACTION_CARD_SELECT: CardSelectAction,
    ACTION_ABILITY_PRESS: AbilityPressAction,
    ACTION_ABILITY_SELECT: AbilitySelectAction,
    ACTION_ABILITY_OPPONENT_PRESS: AbilityOpponentPressAction,
    ACTION_ABILITY_OPPONENT_SELECT: AbilityOpponentSelectAction,
    ACTION_OPPONENT_PRESS: OpponentPressAction,
    ACTION_OPPONENT_SELECT: OpponentSelectAction,
    ACTION_ACTIVE_PLAYER_ROLL: ActivePlayerRollAction,
    ACTION_OPPONENT_ROLL: OpponentRollAction,
    ACTION_REROLL: RerollAction,
    ACTION_REROLL_EFFECT: RerollEffectAction,
    ACTION_BATTLE_END: BattleEndAction,
    ACTION_SKIP_TURN: SkipTurnAction,
    ACTION_DEBUG_SET_BATTLE_DICE_ROLLS: DebugSetBattleDiceRollsAction,
    ACTION_DEBUG_SET_DRAWN_CARD: DebugSetDrawnCardAction,
}
