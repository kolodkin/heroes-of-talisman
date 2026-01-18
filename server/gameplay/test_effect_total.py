"""
Tests for EffectTotal aggregation in Character
"""

from .abilities import BATTLE_HOWL, BOUNCING_ARROW, FREEZE
from .effects import (
    AttackBonusEffect,
    AttackNegBonusEffect,
    RerollDiceEffect,
    SkipTurnEffect,
)
from .gameplay import Character


def test_effect_total_empty():
    """Test that effect property returns empty EffectTotal when no effects"""
    character = Character(
        level=1, health=10, max_health=10, dice=1, attack=2, abilities=[], effects=[]
    )

    effect_total = character.effect

    assert effect_total.attack_bonus == 0
    assert effect_total.attack_neg_bonus == 0
    assert effect_total.skip_next_turn is False
    assert effect_total.reroll_dice_available is False


def test_effect_total_attack_bonus():
    """Test that effect property sums attack bonuses"""
    character = Character(
        level=1,
        health=10,
        max_health=10,
        dice=1,
        attack=2,
        abilities=[],
        effects=[
            AttackBonusEffect(source=BATTLE_HOWL, attack_bonus=2),
            AttackBonusEffect(source=BATTLE_HOWL, attack_bonus=3),
        ],
    )

    effect_total = character.effect

    assert effect_total.attack_bonus == 5
    assert effect_total.attack_neg_bonus == 0


def test_effect_total_attack_neg_bonus():
    """Test that effect property sums attack negative bonuses"""
    character = Character(
        level=1,
        health=10,
        max_health=10,
        dice=1,
        attack=2,
        abilities=[],
        effects=[
            AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-2),
            AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-1),
        ],
    )

    effect_total = character.effect

    assert effect_total.attack_bonus == 0
    assert effect_total.attack_neg_bonus == -3


def test_effect_total_skip_turn():
    """Test that effect property sets skip_next_turn flag"""
    character = Character(
        level=1,
        health=10,
        max_health=10,
        dice=1,
        attack=2,
        abilities=[],
        effects=[SkipTurnEffect(source=FREEZE)],
    )

    effect_total = character.effect

    assert effect_total.skip_next_turn is True


def test_effect_total_reroll_dice_available():
    """Test that effect property sets reroll_dice_available when RerollDiceEffect exists"""
    character = Character(
        level=1,
        health=10,
        max_health=10,
        dice=1,
        attack=2,
        abilities=[],
        effects=[RerollDiceEffect(source=BOUNCING_ARROW)],
    )

    effect_total = character.effect

    assert effect_total.reroll_dice_available is True


def test_effect_total_mixed_effects():
    """Test that effect property correctly aggregates multiple different effects"""
    character = Character(
        level=1,
        health=10,
        max_health=10,
        dice=1,
        attack=2,
        abilities=[],
        effects=[
            AttackBonusEffect(source=BATTLE_HOWL, attack_bonus=2),
            AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-1),
            SkipTurnEffect(source=FREEZE),
            RerollDiceEffect(source=BOUNCING_ARROW),
            AttackBonusEffect(source=BATTLE_HOWL, attack_bonus=1),
        ],
    )

    effect_total = character.effect

    assert effect_total.attack_bonus == 3
    assert effect_total.attack_neg_bonus == -1
    assert effect_total.skip_next_turn is True
    assert effect_total.reroll_dice_available is True


def test_effect_total_is_computed_field():
    """Test that effect property is included in model_dump but excluded from db_model_dump"""
    character = Character(
        level=1,
        health=10,
        max_health=10,
        dice=1,
        attack=2,
        abilities=[],
        effects=[AttackBonusEffect(source=BATTLE_HOWL, attack_bonus=2)],
    )

    # Should be included in regular model_dump
    regular_dump = character.model_dump()
    assert "effect" in regular_dump
    assert regular_dump["effect"]["attack_bonus"] == 2

    # Should be excluded from db_model_dump
    db_dump = character.db_model_dump()
    assert "effect" not in db_dump
