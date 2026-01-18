"""
Action name constants - base module with no dependencies.
"""
from typing import Literal

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
