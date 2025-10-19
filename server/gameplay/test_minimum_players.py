"""
Tests for minimum player requirement.

These tests verify that the game correctly handles scenarios with less than 2 players.
"""

import pytest

from .debug_presets import get_debug_preset, SINGLE_PLAYER
from .models import CHARACTER_SELECT


def test_single_player_preset():
    """Test that single_player preset creates a game with only one player"""
    game = get_debug_preset(SINGLE_PLAYER)

    assert game.stage == CHARACTER_SELECT
    assert len(game.players) == 1
    assert "player1" in game.players
    assert game.players["player1"].name == "player1"


def test_single_player_has_characters():
    """Test that the single player has initialized characters"""
    game = get_debug_preset(SINGLE_PLAYER)

    player = game.players["player1"]
    assert player.characters is not None
    assert len(player.characters) == 3  # knight, archer, mage
