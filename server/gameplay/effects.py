from __future__ import annotations

from typing import Literal, Annotated, Union

from pydantic import Field

from .common import StrictModel

########################################################
# Effect names
########################################################
EFFECT_ATTACK_BONUS = "attack_bonus"
EFFECT_ATTACK_NEG_BONUS = "attack_neg_bonus"
EFFECT_DEFENSE_BONUS = "defense_bonus"
EFFECT_HEAL = "heal"
EFFECT_REROLL_DICE = "reroll_dice"
EFFECT_SKIP_TURN = "skip_turn"
EFFECT_DRAW_CARD = "draw_card"
EFFECT_LEVEL_UP = "level_up"
EFFECT_LEVEL_DOWN = "level_down"
EFFECT_TALISMAN = "talisman"
EFFECT_DARKNESS_RISE = "darkness_rise"
EFFECT_FOG = "fog"
EFFECT_NEUTRALIZE_ITEM = "neutralize_item"

########################################################
# Effect apply_to targets
########################################################
APPLY_TO_SELF = "self"  # Applied to active player's character when ability is selected
APPLY_TO_BATTLE_OPPONENT = "battle_opponent"  # Applied to opponent when battle starts
APPLY_TO_SELECTED_OPPONENT = "selected_opponent"  # Requires ability_opponent_selection stage

APPLY_TO_TARGETS = [APPLY_TO_SELF, APPLY_TO_BATTLE_OPPONENT, APPLY_TO_SELECTED_OPPONENT]
ApplyToTarget = Literal[*APPLY_TO_TARGETS]


class Effect(StrictModel):
    """
    Base class for all effects.
    Effect definitions are stored in ABILITIES_MAP and CARDS_MAP.
    Characters store only string names (active_abilities, active_cards, effects),
    not Effect objects.
    """

    name: Literal["effect"] = "effect"  # Discriminator field for polymorphic serialization
    apply_to: ApplyToTarget  # Who receives this effect


class SkipTurnEffect(Effect):
    """
    Character can't participate in the next turn.
    Disposed after character selection.
    Applied to selected opponent (requires ability_opponent_selection stage).
    """

    name: Literal[EFFECT_SKIP_TURN] = EFFECT_SKIP_TURN
    apply_to: ApplyToTarget = APPLY_TO_SELECTED_OPPONENT
    skip_next_turn: bool = True


class AttackBonusEffect(Effect):
    """
    Character's attack is increased by the value of the effect.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_ATTACK_BONUS] = EFFECT_ATTACK_BONUS
    apply_to: ApplyToTarget = APPLY_TO_SELF
    attack_bonus: int


class DefenseBonusEffect(Effect):
    """
    Character's defense is increased, reducing opponent's battle score.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_DEFENSE_BONUS] = EFFECT_DEFENSE_BONUS
    apply_to: ApplyToTarget = APPLY_TO_SELF
    defense_bonus: int


class RerollDiceEffect(Effect):
    """
    Character's dice are rerolled if lost the battle.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_REROLL_DICE] = EFFECT_REROLL_DICE
    apply_to: ApplyToTarget = APPLY_TO_SELF
    reroll_dice: bool = True


class AttackNegBonusEffect(Effect):
    """
    Character's attack is decreased by the value of the effect.
    Applied to battle opponent (no separate selection required).
    """

    name: Literal[EFFECT_ATTACK_NEG_BONUS] = EFFECT_ATTACK_NEG_BONUS
    apply_to: ApplyToTarget = APPLY_TO_BATTLE_OPPONENT
    attack_neg_bonus: int


class DrawCardEffect(Effect):
    """
    Character draws cards at the start of battle.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_DRAW_CARD] = EFFECT_DRAW_CARD
    apply_to: ApplyToTarget = APPLY_TO_SELF
    draw_count: int = 1


class HealEffect(Effect):
    """
    Character is healed by the specified amount (capped at max_health).
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_HEAL] = EFFECT_HEAL
    apply_to: ApplyToTarget = APPLY_TO_SELF
    heal_amount: int


class LevelUpEffect(Effect):
    """
    Character's level is increased by 1 and health is restored to max.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_LEVEL_UP] = EFFECT_LEVEL_UP
    apply_to: ApplyToTarget = APPLY_TO_SELF
    level_increase: int = 1


class LevelDownEffect(Effect):
    """
    Character's level is decreased by 1.
    Health becomes max(current_health, new_level_max_health).
    No effect if already at level 1.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_LEVEL_DOWN] = EFFECT_LEVEL_DOWN
    apply_to: ApplyToTarget = APPLY_TO_SELF
    level_decrease: int = 1


class TalismanEffect(Effect):
    """
    When the character holding the talisman wins a battle and reduces
    the opponent's health to zero, the opponent dies regardless of level.
    Persistent effect - not disposed at battle end.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_TALISMAN] = EFFECT_TALISMAN
    apply_to: ApplyToTarget = APPLY_TO_SELF


class DarknessRiseEffect(Effect):
    """
    All characters above level 1 across ALL players get skip_turn effect.
    Instant effect - processed at card selection and not persisted.
    Applied to self (but actual processing targets all players' characters).
    """

    name: Literal[EFFECT_DARKNESS_RISE] = EFFECT_DARKNESS_RISE
    apply_to: ApplyToTarget = APPLY_TO_SELF


class FogEffect(Effect):
    """
    Skip the active player's turn unless ALL their alive characters are level 3+.
    Players with all alive characters at level 3+ resist the fog (no effect).
    Players with any alive character below level 3 lose their turn (skip_turn applied to all alive chars).
    Instant effect - processed at card selection and not persisted.
    Only affects the active player (card drawer).
    """

    name: Literal[EFFECT_FOG] = EFFECT_FOG
    apply_to: ApplyToTarget = APPLY_TO_SELF


class NeutralizeItemEffect(Effect):
    """
    Removes one active card (item) from the target character.
    Instant effect - processed at ability opponent selection and not persisted.
    Applied to selected opponent (requires ability_opponent_selection stage).
    """

    name: Literal[EFFECT_NEUTRALIZE_ITEM] = EFFECT_NEUTRALIZE_ITEM
    apply_to: ApplyToTarget = APPLY_TO_SELECTED_OPPONENT


# Define EffectUnion for discriminated union of all effect types (without base classes)
EffectUnion = Annotated[
    Union[AttackBonusEffect, AttackNegBonusEffect, DefenseBonusEffect, HealEffect, LevelDownEffect, LevelUpEffect, RerollDiceEffect, SkipTurnEffect, DrawCardEffect, TalismanEffect, DarknessRiseEffect, FogEffect, NeutralizeItemEffect],
    Field(discriminator="name"),
]


class EffectTotal(StrictModel):
    """
    Aggregated effect totals for a character.
    Combines all active effects into a single summary.
    """

    attack_bonus: int = 0
    attack_neg_bonus: int = 0
    defense_bonus: int = 0
    heal_amount: int = 0
    level_up_amount: int = 0
    skip_next_turn: bool = False
    reroll_dice_available: bool = False
    draw_card_count: int = 0
    has_talisman: bool = False
