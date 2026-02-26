"""
Tests for EffectTotal aggregation in Character.

EffectTotal is now computed by looking up definitions from ABILITIES_MAP and CARDS_MAP
based on string names stored in active_abilities, active_cards, and effects lists.
"""

from .abilities import ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW
from .effects import EFFECT_SKIP_TURN
from .cards import CARD_METAL_ARMOR, CARD_SACRED_SWORD, CARD_TALISMAN
from .gameplay import Character


def test_effect_total_empty():
    """Test that effect property returns empty EffectTotal when no effects"""
    character = Character(
        level=1, health=10, max_health=10, dice=1, attack=2, abilities=[]
    )

    effect_total = character.effect

    assert effect_total.attack_bonus == 0
    assert effect_total.attack_neg_bonus == 0
    assert effect_total.skip_next_turn is False
    assert effect_total.reroll_dice_available is False
    assert effect_total.defense_bonus == 0
    assert effect_total.has_talisman is False


def test_effect_total_attack_bonus_from_ability():
    """Test that battle_howl ability provides attack bonus"""
    character = Character(
        level=1, health=10, max_health=10, dice=1, attack=2,
        abilities=[],
        active_abilities=[ABILITY_BATTLE_HOWL],
    )

    effect_total = character.effect

    assert effect_total.attack_bonus == 2
    assert effect_total.attack_neg_bonus == 0


def test_effect_total_attack_bonus_from_card():
    """Test that sacred_sword card provides attack bonus"""
    character = Character(
        level=1, health=10, max_health=10, dice=1, attack=2,
        abilities=[],
        active_cards=[CARD_SACRED_SWORD],
    )

    effect_total = character.effect

    assert effect_total.attack_bonus == 3


def test_effect_total_defense_bonus_from_card():
    """Test that metal_armor card provides defense bonus"""
    character = Character(
        level=1, health=10, max_health=10, dice=1, attack=2,
        abilities=[],
        active_cards=[CARD_METAL_ARMOR],
    )

    effect_total = character.effect

    assert effect_total.defense_bonus == 2


def test_effect_total_skip_turn():
    """Test that skip_turn effect string sets skip_next_turn flag"""
    character = Character(
        level=1, health=10, max_health=10, dice=1, attack=2,
        abilities=[],
        effects=[EFFECT_SKIP_TURN],
    )

    effect_total = character.effect

    assert effect_total.skip_next_turn is True


def test_effect_total_reroll_dice_available():
    """Test that bouncing_arrow ability provides reroll_dice_available"""
    character = Character(
        level=1, health=10, max_health=10, dice=1, attack=2,
        abilities=[],
        active_abilities=[ABILITY_BOUNCING_ARROW],
    )

    effect_total = character.effect

    assert effect_total.reroll_dice_available is True


def test_effect_total_talisman():
    """Test that talisman card provides has_talisman flag"""
    character = Character(
        level=1, health=10, max_health=10, dice=1, attack=2,
        abilities=[],
        active_cards=[CARD_TALISMAN],
    )

    effect_total = character.effect

    assert effect_total.has_talisman is True


def test_effect_total_mixed_effects():
    """Test that effect property correctly aggregates multiple different effect sources"""
    character = Character(
        level=1, health=10, max_health=10, dice=1, attack=2,
        abilities=[],
        active_abilities=[ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW],
        active_cards=[CARD_METAL_ARMOR, CARD_SACRED_SWORD],
        effects=[EFFECT_SKIP_TURN],
    )

    effect_total = character.effect

    # battle_howl gives +2 attack, sacred_sword gives +3 attack
    assert effect_total.attack_bonus == 5
    assert effect_total.defense_bonus == 2
    assert effect_total.skip_next_turn is True
    assert effect_total.reroll_dice_available is True


def test_effect_total_is_computed_field():
    """Test that effect property is included in model_dump but excluded from db_model_dump"""
    character = Character(
        level=1, health=10, max_health=10, dice=1, attack=2,
        abilities=[],
        active_abilities=[ABILITY_BATTLE_HOWL],
    )

    # Should be included in regular model_dump
    regular_dump = character.model_dump()
    assert "effect" in regular_dump
    assert regular_dump["effect"]["attack_bonus"] == 2

    # Should be excluded from db_model_dump
    db_dump = character.db_model_dump()
    assert "effect" not in db_dump
