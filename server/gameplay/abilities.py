from __future__ import annotations

from typing import Literal

from pydantic import Field

from .common import StrictModel
from .effects import (
    EffectUnion,
    AttackBonusEffect,
    RerollDiceEffect,
    SkipTurnEffect,
    APPLY_TO_SELECTED_OPPONENT,
)

########################################################
# Ability names
########################################################
ABILITY_BATTLE_HOWL = "battle_howl"
ABILITY_BOUNCING_ARROW = "bouncing_arrow"
ABILITY_FREEZE = "freeze"
ABILITIES_NAMES: list[str] = [ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW, ABILITY_FREEZE]
AbilityName = Literal[*ABILITIES_NAMES]


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
            AttackBonusEffect(attack_bonus=2),
        ],
    ),
    ABILITY_BOUNCING_ARROW: Ability(
        name=ABILITY_BOUNCING_ARROW,
        effects=[
            RerollDiceEffect(),
        ],
    ),
    ABILITY_FREEZE: Ability(
        name=ABILITY_FREEZE,
        effects=[
            SkipTurnEffect(),
        ],
    ),
}
