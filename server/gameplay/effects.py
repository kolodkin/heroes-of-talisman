from __future__ import annotations

from typing import Literal, Annotated, Union, Self

from pydantic import Field, model_validator

from .common import StrictModel
from .actions_names import (
    ActionName,
    # Action name constants for dispose_actions
    ACTION_CHARACTER_SELECT,
    ACTION_CARD_SELECT,
    ACTION_BATTLE_END,
    ACTION_REROLL_EFFECT,
)

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
EFFECT_TALISMAN = "talisman"

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
    Each effect specifies when it should be disposed via dispose_actions field.
    Each effect specifies who receives the effect via apply_to field.
    """

    name: Literal["effect"] = "effect"  # Discriminator field for polymorphic serialization
    source: str  # AbilityName - using str to avoid circular import
    dispose_actions: list[ActionName]  # Action names when this effect should be disposed
    apply_to: ApplyToTarget  # Who receives this effect

    @model_validator(mode="after")
    def validate_source(self) -> Self:
        """Validate that source is valid for this effect type"""
        from .abilities import EFFECTS_SOURCE_ABILITY_MAP
        from .cards import EFFECTS_SOURCE_CARD_MAP

        ability_sources = EFFECTS_SOURCE_ABILITY_MAP.get(self.name, set())
        card_sources = EFFECTS_SOURCE_CARD_MAP.get(self.name, set())
        valid_sources = ability_sources | card_sources

        if self.source not in valid_sources and len(valid_sources) > 0:
            raise ValueError(
                f"Invalid source '{self.source}' for {self.__class__.__name__}. "
                f"Valid sources: {valid_sources}"
            )
        return self


class SkipTurnEffect(Effect):
    """
    Character can't participate in the next turn.
    Disposed after character selection.
    Applied to selected opponent (requires ability_opponent_selection stage).
    """

    name: Literal[EFFECT_SKIP_TURN] = EFFECT_SKIP_TURN
    dispose_actions: list[ActionName] = [ACTION_CHARACTER_SELECT]
    apply_to: ApplyToTarget = APPLY_TO_SELECTED_OPPONENT
    skip_next_turn: bool = True


class AttackBonusEffect(Effect):
    """
    Character's attack is increased by the value of the effect.
    Disposed at battle end.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_ATTACK_BONUS] = EFFECT_ATTACK_BONUS
    dispose_actions: list[ActionName] = [ACTION_BATTLE_END]
    apply_to: ApplyToTarget = APPLY_TO_SELF
    attack_bonus: int


class DefenseBonusEffect(Effect):
    """
    Character's defense is increased, reducing opponent's battle score.
    Disposed at battle end.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_DEFENSE_BONUS] = EFFECT_DEFENSE_BONUS
    dispose_actions: list[ActionName] = [ACTION_BATTLE_END]
    apply_to: ApplyToTarget = APPLY_TO_SELF
    defense_bonus: int


class RerollDiceEffect(Effect):
    """
    Character's dice are rerolled if lost the battle.
    Disposed at battle end or when the reroll effect action is used.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_REROLL_DICE] = EFFECT_REROLL_DICE
    dispose_actions: list[ActionName] = [ACTION_BATTLE_END, ACTION_REROLL_EFFECT]
    apply_to: ApplyToTarget = APPLY_TO_SELF
    reroll_dice: bool = True


class AttackNegBonusEffect(Effect):
    """
    Character's attack is decreased by the value of the effect.
    Disposed at battle end.
    Applied to battle opponent (no separate selection required).
    """

    name: Literal[EFFECT_ATTACK_NEG_BONUS] = EFFECT_ATTACK_NEG_BONUS
    dispose_actions: list[ActionName] = [ACTION_BATTLE_END]
    apply_to: ApplyToTarget = APPLY_TO_BATTLE_OPPONENT
    attack_neg_bonus: int


class DrawCardEffect(Effect):
    """
    Character draws cards at the start of battle.
    Disposed at battle end.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_DRAW_CARD] = EFFECT_DRAW_CARD
    dispose_actions: list[ActionName] = [ACTION_BATTLE_END]
    apply_to: ApplyToTarget = APPLY_TO_SELF
    draw_count: int = 1


class HealEffect(Effect):
    """
    Character is healed by the specified amount (capped at max_health).
    Disposed at card selection (instant effect).
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_HEAL] = EFFECT_HEAL
    dispose_actions: list[ActionName] = [ACTION_CARD_SELECT]
    apply_to: ApplyToTarget = APPLY_TO_SELF
    heal_amount: int


class LevelUpEffect(Effect):
    """
    Character's level is increased by 1 and health is restored to max.
    Disposed at card selection (instant effect).
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_LEVEL_UP] = EFFECT_LEVEL_UP
    dispose_actions: list[ActionName] = [ACTION_CARD_SELECT]
    apply_to: ApplyToTarget = APPLY_TO_SELF
    level_increase: int = 1


class TalismanEffect(Effect):
    """
    When the character holding the talisman wins a battle and reduces
    the opponent's health to zero, the opponent dies regardless of level.
    Persistent effect - not disposed at battle end.
    Applied to self (active player's character).
    """

    name: Literal[EFFECT_TALISMAN] = EFFECT_TALISMAN
    dispose_actions: list[ActionName] = []
    apply_to: ApplyToTarget = APPLY_TO_SELF


# Define EffectUnion for discriminated union of all effect types (without base classes)
EffectUnion = Annotated[
    Union[AttackBonusEffect, AttackNegBonusEffect, DefenseBonusEffect, HealEffect, LevelUpEffect, RerollDiceEffect, SkipTurnEffect, DrawCardEffect, TalismanEffect],
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
