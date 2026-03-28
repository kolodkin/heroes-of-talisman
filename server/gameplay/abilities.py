from __future__ import annotations

from typing import Literal

from pydantic import Field

from .common import StrictModel
from .effects import (
    EffectUnion,
    AttackBonusEffect,
    AttackNegBonusEffect,
    BurningArrowEffect,
    DrawCardEffect,
    NeutralizeItemEffect,
    RerollDiceEffect,
    SkipTurnEffect,
)

########################################################
# Ability names
########################################################
ABILITY_BATTLE_HOWL = "battle_howl"
ABILITY_BOUNCING_ARROW = "bouncing_arrow"
ABILITY_BOUNCING_ARROW_L2 = "bouncing_arrow_l2"
ABILITY_BOUNCING_ARROW_L3 = "bouncing_arrow_l3"
ABILITY_BURNING_ARROW = "burning_arrow"
ABILITY_FREEZE = "freeze"
ABILITY_DISARM = "disarm"
ABILITY_STORM = "storm"
ABILITY_DRAGON_BREATH = "dragon_breath"
ABILITIES_NAMES: list[str] = [ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW, ABILITY_BOUNCING_ARROW_L2, ABILITY_BOUNCING_ARROW_L3, ABILITY_BURNING_ARROW, ABILITY_FREEZE, ABILITY_DISARM, ABILITY_STORM, ABILITY_DRAGON_BREATH]
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
    ABILITY_BOUNCING_ARROW_L2: Ability(
        name=ABILITY_BOUNCING_ARROW_L2,
        effects=[
            RerollDiceEffect(),
        ],
    ),
    ABILITY_BOUNCING_ARROW_L3: Ability(
        name=ABILITY_BOUNCING_ARROW_L3,
        effects=[
            RerollDiceEffect(),
        ],
    ),
    ABILITY_BURNING_ARROW: Ability(
        name=ABILITY_BURNING_ARROW,
        effects=[
            BurningArrowEffect(),
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
    ABILITY_STORM: Ability(
        name=ABILITY_STORM,
        effects=[
            AttackNegBonusEffect(attack_neg_bonus=-2),
        ],
    ),
    ABILITY_DRAGON_BREATH: Ability(
        name=ABILITY_DRAGON_BREATH,
        effects=[
            NeutralizeItemEffect(),
        ],
    ),
}


def get_ability_effects(ability_name: AbilityName) -> list[EffectUnion]:
    """Look up effects for an ability by name from ABILITIES_MAP"""
    ability = ABILITIES_MAP.get(ability_name)
    return ability.effects if ability else []
