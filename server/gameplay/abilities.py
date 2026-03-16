from __future__ import annotations

from typing import Literal

from pydantic import Field

from .common import StrictModel
from .effects import (
    EffectUnion,
    AttackBonusEffect,
    DrawCardEffect,
    RerollDiceEffect,
    SkipTurnEffect,
)

########################################################
# Ability names
########################################################
ABILITY_BATTLE_HOWL = "battle_howl"
ABILITY_BOUNCING_ARROW = "bouncing_arrow"
ABILITY_FREEZE = "freeze"
ABILITY_DISARM = "disarm"
ABILITIES_NAMES: list[str] = [ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW, ABILITY_FREEZE, ABILITY_DISARM]
AbilityName = Literal[*ABILITIES_NAMES]


class Ability(StrictModel):
    name: str
    effects: list[EffectUnion] = Field(default_factory=list)  # effects that are applied when the ability is used


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
    ABILITY_DISARM: Ability(
        name=ABILITY_DISARM,
        effects=[
            DrawCardEffect(),
        ],
    ),
}


def get_ability_effects(ability_name: AbilityName) -> list[EffectUnion]:
    """Look up effects for an ability by name from ABILITIES_MAP"""
    ability = ABILITIES_MAP.get(ability_name)
    return ability.effects if ability else []
