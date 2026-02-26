"""
Tests for effect definitions (source validation removed, effects are now definition-only objects).
Effects no longer have source or dispose_actions fields.
"""

from .effects import (
    AttackBonusEffect,
    RerollDiceEffect,
    SkipTurnEffect,
    EFFECT_ATTACK_BONUS,
    EFFECT_REROLL_DICE,
    EFFECT_SKIP_TURN,
)


def test_effects_have_correct_names():
    """Test that effect instances have correct name discriminators"""
    attack_bonus = AttackBonusEffect(attack_bonus=2)
    assert attack_bonus.name == EFFECT_ATTACK_BONUS
    assert attack_bonus.attack_bonus == 2

    reroll_dice = RerollDiceEffect()
    assert reroll_dice.name == EFFECT_REROLL_DICE
    assert reroll_dice.reroll_dice is True

    skip_turn = SkipTurnEffect()
    assert skip_turn.name == EFFECT_SKIP_TURN
    assert skip_turn.skip_next_turn is True
