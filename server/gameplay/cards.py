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
    """
    Card model representing gameplay cards that players can draw and use.

    Important: Card effects are PERSISTENT and last for the entire game (or until character dies).
    This is different from ability effects which are disposed after each battle.

    To make effects persistent, set dispose_actions=[] when creating the effect.
    """
    name: str
    effects: list[EffectUnion] = Field(default_factory=list)  # effects that are applied when the card is used


CARDS_MAP: dict[CardName, Card] = {
    METAL_ARMOR: Card(
        name=METAL_ARMOR,
        effects=[
            # Card effects persist across battles (empty dispose_actions)
            # Unlike ability effects which dispose after BATTLE_END_ACTION
            DefenseBonusEffect(source=METAL_ARMOR, defense_bonus=2, dispose_actions=[]),
        ],
    ),
}
