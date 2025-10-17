"""
Tests for GamePlay models.

These tests verify model behavior including computed properties.
"""

import pytest

from .models import (
    CharacterCard,
    CHARACTER_DEFAULT_STATS,
    KNIGHT,
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
