from __future__ import annotations

from typing import Literal

from pydantic import Field

from .common import StrictModel
from .effects import (
    # Effect name constants for EFFECTS_SOURCE_ABILITY_MAP
    EFFECT_ATTACK_BONUS,
    EFFECT_ATTACK_NEG_BONUS,
    EFFECT_REROLL_DICE,
    EFFECT_SKIP_TURN,
    EFFECT_DRAW_CARD,
    # Apply to constants
    APPLY_TO_SELECTED_OPPONENT,
)

########################################################
# Ability names - defined before imports from effects to avoid circular dependency
########################################################
ABILITY_BATTLE_HOWL = "battle_howl"
ABILITY_BOUNCING_ARROW = "bouncing_arrow"
ABILITY_FREEZE = "freeze"
ABILITIES_NAMES: list[str] = [ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW, ABILITY_FREEZE]
AbilityName = Literal[*ABILITIES_NAMES]

########################################################
# Effect-to-Source mapping
########################################################
# Defines which abilities can create which effects
# This is used for validation to ensure effects have valid source abilities
EFFECTS_SOURCE_ABILITY_MAP: dict[str, set[str]] = {
    EFFECT_ATTACK_BONUS: {ABILITY_BATTLE_HOWL},  # AttackBonusEffect can come from ABILITY_BATTLE_HOWL
    EFFECT_ATTACK_NEG_BONUS: set(),  # AttackNegBonusEffect - TBD: add abilities that grant attack penalty
    EFFECT_REROLL_DICE: {ABILITY_BOUNCING_ARROW},  # RerollDiceEffect can come from ABILITY_BOUNCING_ARROW
    EFFECT_SKIP_TURN: {ABILITY_FREEZE},  # SkipTurnEffect can come from ABILITY_FREEZE
    EFFECT_DRAW_CARD: set(),  # DrawCardEffect - TBD: add abilities that grant card draw
}

# Import Effect classes after defining constants to avoid circular import
from .effects import (
    EffectUnion,
    AttackBonusEffect,
    RerollDiceEffect,
    SkipTurnEffect,
)


class Ability(StrictModel):
    name: str
    effects: list[EffectUnion] = Field(default_factory=list)  # effects that are applied when the ability is used

    @property
    def requires_opponent_selection(self) -> bool:
        """Check if any effect requires opponent selection (via ability_opponent_selection stage)"""
        return any(effect.apply_to == APPLY_TO_SELECTED_OPPONENT for effect in self.effects)


ABILITIES_MAP: dict[AbilityName, Ability] = {
    ABILITY_BATTLE_HOWL: Ability(
        name=ABILITY_BATTLE_HOWL,
        effects=[
            AttackBonusEffect(source=ABILITY_BATTLE_HOWL, attack_bonus=2),
        ],
    ),
    ABILITY_BOUNCING_ARROW: Ability(
        name=ABILITY_BOUNCING_ARROW,
        effects=[
            RerollDiceEffect(source=ABILITY_BOUNCING_ARROW),
        ],
    ),
    ABILITY_FREEZE: Ability(
        name=ABILITY_FREEZE,
        effects=[
            SkipTurnEffect(source=ABILITY_FREEZE),
        ],
    ),
}
