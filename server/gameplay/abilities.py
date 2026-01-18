from __future__ import annotations

from typing import Literal

from pydantic import Field

from .common import StrictModel
from .effects import (
    # Effect name constants for EFFECTS_SOURCE_ABILITY_MAP
    ATTACK_BONUS,
    ATTACK_NEG_BONUS,
    REROLL_DICE,
    SKIP_TURN,
    DRAW_CARD,
    # Apply to constants
    APPLY_TO_SELECTED_OPPONENT,
)

########################################################
# Ability names - defined before imports from effects to avoid circular dependency
########################################################
BATTLE_HOWL = "battle_howl"
BOUNCING_ARROW = "bouncing_arrow"
FREEZE = "freeze"
ABILITIES_NAMES: list[str] = [BATTLE_HOWL, BOUNCING_ARROW, FREEZE]
AbilityName = Literal[*ABILITIES_NAMES]

########################################################
# Effect-to-Source mapping
########################################################
# Defines which abilities can create which effects
# This is used for validation to ensure effects have valid source abilities
EFFECTS_SOURCE_ABILITY_MAP: dict[str, set[str]] = {
    ATTACK_BONUS: {BATTLE_HOWL},  # AttackBonusEffect can come from BATTLE_HOWL
    ATTACK_NEG_BONUS: set(),  # AttackNegBonusEffect - TBD: add abilities that grant attack penalty
    REROLL_DICE: {BOUNCING_ARROW},  # RerollDiceEffect can come from BOUNCING_ARROW
    SKIP_TURN: {FREEZE},  # SkipTurnEffect can come from FREEZE
    DRAW_CARD: set(),  # DrawCardEffect - TBD: add abilities that grant card draw
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
    BATTLE_HOWL: Ability(
        name=BATTLE_HOWL,
        effects=[
            AttackBonusEffect(source=BATTLE_HOWL, attack_bonus=2),
        ],
    ),
    BOUNCING_ARROW: Ability(
        name=BOUNCING_ARROW,
        effects=[
            RerollDiceEffect(source=BOUNCING_ARROW),
        ],
    ),
    FREEZE: Ability(
        name=FREEZE,
        effects=[
            SkipTurnEffect(source=FREEZE),
        ],
    ),
}
