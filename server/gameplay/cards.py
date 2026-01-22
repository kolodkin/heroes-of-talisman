from __future__ import annotations

from typing import Literal

from pydantic import Field

from .common import StrictModel
from .effects import (
    # Effect name constants for EFFECTS_SOURCE_CARD_MAP
    DEFENSE_BONUS,
    ATTACK_BONUS,
    # Apply to constants
    APPLY_TO_SELF,
)

########################################################
# Card names - defined before imports from effects to avoid circular dependency
########################################################
METAL_ARMOR = "metal_armor"
SACRED_SWORD = "sacred_sord"
CARDS_NAMES: list[str] = [METAL_ARMOR, SACRED_SWORD]
CardName = Literal[*CARDS_NAMES]

########################################################
# Effect-to-Source mapping
########################################################
# Defines which cards can create which effects
# This is used for validation to ensure effects have valid source cards
EFFECTS_SOURCE_CARD_MAP: dict[str, set[str]] = {
    DEFENSE_BONUS: {METAL_ARMOR},
    ATTACK_BONUS: {SACRED_SWORD},
}

# Import Effect classes after defining constants to avoid circular import
from .effects import (
    EffectUnion,
    DefenseBonusEffect,
    AttackBonusEffect,
)


class Card(StrictModel):
    name: str
    effects: list[EffectUnion] = Field(default_factory=list)
    restricted_characters: list[str] = Field(default_factory=list)


CARDS_MAP: dict[CardName, Card] = {
    METAL_ARMOR: Card(
        name=METAL_ARMOR,
        effects=[
            DefenseBonusEffect(source=METAL_ARMOR, defense_bonus=2, dispose_actions=[]),
        ],
    ),
    SACRED_SWORD: Card(
        name=SACRED_SWORD,
        effects=[
            AttackBonusEffect(source=SACRED_SWORD, attack_bonus=3, dispose_actions=[]),
        ],
        restricted_characters=["archer"],
    ),
}
