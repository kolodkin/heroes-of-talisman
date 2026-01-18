from __future__ import annotations

from pydantic import Field

from .gameplay import (
    StrictModel,
    AbilityName,
    BATTLE_HOWL,
    BOUNCING_ARROW,
    FREEZE,
    APPLY_TO_SELECTED_OPPONENT,
)
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
