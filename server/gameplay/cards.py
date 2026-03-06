from __future__ import annotations

from typing import Literal

from pydantic import Field

from .common import StrictModel
from .effects import (
    EffectUnion,
    DefenseBonusEffect,
    AttackBonusEffect,
    HealEffect,
    LevelUpEffect,
    TalismanEffect,
)

########################################################
# Card names
########################################################
CARD_METAL_ARMOR = "metal_armor"
CARD_SACRED_SWORD = "sacred_sord"
CARD_GOLDEN_APPLE = "golden_apple"
CARD_MAGIC_BALL = "magic_ball"
CARD_TALISMAN = "talisman"
CARDS_NAMES: list[str] = [CARD_METAL_ARMOR, CARD_SACRED_SWORD, CARD_GOLDEN_APPLE, CARD_MAGIC_BALL, CARD_TALISMAN]
CardName = Literal[*CARDS_NAMES]


class Card(StrictModel):
    name: str
    effects: list[EffectUnion] = Field(default_factory=list)
    restricted_characters: list[str] = Field(default_factory=list)


CARDS_MAP: dict[CardName, Card] = {
    CARD_METAL_ARMOR: Card(
        name=CARD_METAL_ARMOR,
        effects=[
            DefenseBonusEffect(defense_bonus=2),
        ],
    ),
    CARD_SACRED_SWORD: Card(
        name=CARD_SACRED_SWORD,
        effects=[
            AttackBonusEffect(attack_bonus=3),
        ],
        restricted_characters=["archer"],
    ),
    CARD_GOLDEN_APPLE: Card(
        name=CARD_GOLDEN_APPLE,
        effects=[
            HealEffect(heal_amount=1),
        ],
    ),
    CARD_MAGIC_BALL: Card(
        name=CARD_MAGIC_BALL,
        effects=[
            LevelUpEffect(),
        ],
    ),
    CARD_TALISMAN: Card(
        name=CARD_TALISMAN,
        effects=[
            TalismanEffect(),
        ],
    ),
}
