"""
Tests for effect source validation
"""

import pytest
from pydantic import ValidationError

from .abilities import ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW, ABILITY_FREEZE
from .effects import (
    AttackBonusEffect,
    AttackNegBonusEffect,
    RerollDiceEffect,
    SkipTurnEffect,
)


def test_effects_accept_valid_sources():
    """Test that all effects accept their designated valid sources"""
    # AttackBonusEffect accepts BATTLE_HOWL
    attack_bonus = AttackBonusEffect(source=ABILITY_BATTLE_HOWL, attack_bonus=2)
    assert attack_bonus.source == BATTLE_HOWL
    assert attack_bonus.attack_bonus == 2

    # RerollDiceEffect accepts BOUNCING_ARROW
    reroll_dice = RerollDiceEffect(source=ABILITY_BOUNCING_ARROW)
    assert reroll_dice.source == BOUNCING_ARROW
    assert reroll_dice.reroll_dice is True

    # SkipTurnEffect accepts FREEZE
    skip_turn = SkipTurnEffect(source=ABILITY_FREEZE)
    assert skip_turn.source == FREEZE
    assert skip_turn.skip_next_turn is True


def test_effects_reject_invalid_sources():
    """Test that effects reject sources that are not designated for them"""
    # AttackBonusEffect rejects non-BATTLE_HOWL sources
    with pytest.raises(ValidationError) as exc_info:
        AttackBonusEffect(source=ABILITY_FREEZE, attack_bonus=2)
    assert "Invalid source" in str(exc_info.value)

    # RerollDiceEffect rejects non-BOUNCING_ARROW sources
    with pytest.raises(ValidationError) as exc_info:
        RerollDiceEffect(source=ABILITY_BATTLE_HOWL)
    assert "Invalid source" in str(exc_info.value)

    # SkipTurnEffect rejects non-FREEZE sources
    with pytest.raises(ValidationError) as exc_info:
        SkipTurnEffect(source=ABILITY_BOUNCING_ARROW)
    assert "Invalid source" in str(exc_info.value)
