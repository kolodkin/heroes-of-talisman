from __future__ import annotations

from typing import Literal, Annotated, Union, Self

from pydantic import Field, model_validator

from .models import (
    StrictModel,
    ActionName,
    ApplyToTarget,
    # Effect name constants
    ATTACK_BONUS,
    ATTACK_NEG_BONUS,
    REROLL_DICE,
    SKIP_TURN,
    DRAW_CARD,
    # Action name constants for dispose_actions
    CHARACTER_SELECT_ACTION,
    BATTLE_END_ACTION,
    ACTION_REROLL_EFFECT,
    # Apply to constants
    APPLY_TO_SELF,
    APPLY_TO_BATTLE_OPPONENT,
    APPLY_TO_SELECTED_OPPONENT,
)
from .abilities import (
    AbilityName,
    BATTLE_HOWL,
    BOUNCING_ARROW,
    FREEZE,
    EFFECTS_SOURCE_ABILITY_MAP,
)


class Effect(StrictModel):
    """
    Base class for all effects.
    Each effect specifies when it should be disposed via dispose_actions field.
    Each effect specifies who receives the effect via apply_to field.
    """

    name: Literal["effect"] = "effect"  # Discriminator field for polymorphic serialization
    source: AbilityName
    dispose_actions: list[ActionName]  # Action names when this effect should be disposed
    apply_to: ApplyToTarget  # Who receives this effect

    @model_validator(mode="after")
    def validate_source(self) -> Self:
        """Validate that source is valid for this effect type"""
        valid_sources = EFFECTS_SOURCE_ABILITY_MAP.get(self.name, set())
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

    name: Literal[SKIP_TURN] = SKIP_TURN
    dispose_actions: list[ActionName] = [CHARACTER_SELECT_ACTION]
    apply_to: ApplyToTarget = APPLY_TO_SELECTED_OPPONENT
    skip_next_turn: bool = True


class AttackBonusEffect(Effect):
    """
    Character's attack is increased by the value of the effect.
    Disposed at battle end.
    Applied to self (active player's character).
    """

    name: Literal[ATTACK_BONUS] = ATTACK_BONUS
    dispose_actions: list[ActionName] = [BATTLE_END_ACTION]
    apply_to: ApplyToTarget = APPLY_TO_SELF
    attack_bonus: int


class RerollDiceEffect(Effect):
    """
    Character's dice are rerolled if lost the battle.
    Disposed at battle end or when the reroll effect action is used.
    Applied to self (active player's character).
    """

    name: Literal[REROLL_DICE] = REROLL_DICE
    dispose_actions: list[ActionName] = [BATTLE_END_ACTION, ACTION_REROLL_EFFECT]
    apply_to: ApplyToTarget = APPLY_TO_SELF
    reroll_dice: bool = True


class AttackNegBonusEffect(Effect):
    """
    Character's attack is decreased by the value of the effect.
    Disposed at battle end.
    Applied to battle opponent (no separate selection required).
    """

    name: Literal[ATTACK_NEG_BONUS] = ATTACK_NEG_BONUS
    dispose_actions: list[ActionName] = [BATTLE_END_ACTION]
    apply_to: ApplyToTarget = APPLY_TO_BATTLE_OPPONENT
    attack_neg_bonus: int


class DrawCardEffect(Effect):
    """
    Character draws cards at the start of battle.
    Disposed at battle end.
    Applied to self (active player's character).
    """

    name: Literal[DRAW_CARD] = DRAW_CARD
    dispose_actions: list[ActionName] = [BATTLE_END_ACTION]
    apply_to: ApplyToTarget = APPLY_TO_SELF
    draw_count: int = 1


# Define EffectUnion for discriminated union of all effect types (without base classes)
EffectUnion = Annotated[
    Union[AttackBonusEffect, AttackNegBonusEffect, RerollDiceEffect, SkipTurnEffect, DrawCardEffect],
    Field(discriminator="name"),
]


class EffectTotal(StrictModel):
    """
    Aggregated effect totals for a character.
    Combines all active effects into a single summary.
    """

    attack_bonus: int = 0
    attack_neg_bonus: int = 0
    skip_next_turn: bool = False
    reroll_dice_available: bool = False
    draw_card_count: int = 0
