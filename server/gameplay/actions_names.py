"""
Action name constants - base module with no dependencies.
"""
from typing import Literal

########################################################
# Actions
########################################################
ACTION_CONNECT = "connect"
ACTION_LEAVE = "leave"
ACTION_DISCONNECT = "disconnect"
ACTION_CHARACTER_PRESS = "character_press"
ACTION_CHARACTER_SELECT = "character_select"
ACTION_CARD_DRAW = "card_draw"
ACTION_CARD_SELECT = "card_select"
ACTION_ABILITY_PRESS = "ability_press"
ACTION_ABILITY_SELECT = "ability_select"
ACTION_ABILITY_OPPONENT_PRESS = "ability_opponent_press"
ACTION_ABILITY_OPPONENT_SELECT = "ability_opponent_select"
ACTION_ABILITY_ITEM_PRESS = "ability_item_press"
ACTION_ABILITY_ITEM_SELECT = "ability_item_select"
ACTION_OPPONENT_PRESS = "opponent_press"
ACTION_OPPONENT_SELECT = "opponent_select"
ACTION_ACTIVE_PLAYER_ROLL = "active_player_roll"
ACTION_OPPONENT_ROLL = "opponent_roll"
ACTION_REROLL = "action_reroll"
ACTION_REROLL_EFFECT = "action_reroll_effect"
ACTION_BATTLE_END = "battle_end"
ACTION_SKIP_TURN = "skip_turn"
ACTION_DEBUG_SET_BATTLE_DICE_ROLLS = "debug_set_battle_dice_rolls"
ACTION_DEBUG_SET_DRAWN_CARD = "debug_set_drawn_card"

ACTION_NAMES = [
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
]
ActionName = Literal[*ACTION_NAMES]
