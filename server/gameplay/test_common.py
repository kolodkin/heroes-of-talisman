"""
Tests for GamePlay models.

These tests verify model behavior including computed properties.
"""

import pytest

from .common import KNIGHT
from .abilities import ABILITIES_MAP, BATTLE_HOWL, BOUNCING_ARROW, FREEZE
from .gameplay import (
    Character,
    CHARACTER_DEFAULT_STATS,
    init_characters,
    KNIGHT_L1_DEFAULT_HEALTH,
)


def test_character_is_alive_when_health_positive():
    """Test character is alive when health > 0"""
    characters = init_characters()
    assert characters[KNIGHT].health == KNIGHT_L1_DEFAULT_HEALTH
    assert characters[KNIGHT].is_alive is True


def test_character_is_dead_when_health_zero():
    """Test character is dead when health = 0"""
    characters = init_characters()
    characters[KNIGHT].health = 0
    assert characters[KNIGHT].is_alive is False


def test_ability_requires_opponent_selection():
    """Test which abilities require opponent selection (only FREEZE with SkipTurnEffect)"""
    # Only FREEZE requires opponent selection (has SkipTurnEffect)
    assert ABILITIES_MAP[FREEZE].requires_opponent_selection is True

    # Other abilities are applied to battle opponent automatically
    assert ABILITIES_MAP[BATTLE_HOWL].requires_opponent_selection is False
    assert ABILITIES_MAP[BOUNCING_ARROW].requires_opponent_selection is False
