from __future__ import annotations

from typing import Literal

from pydantic import Field

from .common import StrictModel
from .effects import (
    # Effect name constants for EFFECTS_SOURCE_CARD_MAP
    DEFENSE_BONUS,
    # Apply to constants
    APPLY_TO_SELF,
)

########################################################
# Card names - defined before imports from effects to avoid circular dependency
########################################################
METAL_ARMOR = "metal_armor"
CARDS_NAMES: list[str] = [METAL_ARMOR]
CardName = Literal[*CARDS_NAMES]

########################################################
# Effect-to-Source mapping
########################################################
# Defines which cards can create which effects
# This is used for validation to ensure effects have valid source cards
EFFECTS_SOURCE_CARD_MAP: dict[str, set[str]] = {
    DEFENSE_BONUS: {METAL_ARMOR},  # DefenseBonusEffect can come from METAL_ARMOR
}

# Import Effect classes after defining constants to avoid circular import
from .effects import (
    EffectUnion,
    DefenseBonusEffect,
)


class Card(StrictModel):
    name: str
    effects: list[EffectUnion] = Field(default_factory=list)


CARDS_MAP: dict[CardName, Card] = {
    METAL_ARMOR: Card(
        name=METAL_ARMOR,
        effects=[
            DefenseBonusEffect(source=METAL_ARMOR, defense_bonus=2, dispose_actions=[]),
        ],
    ),
}
