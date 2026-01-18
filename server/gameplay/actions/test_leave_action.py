"""
Tests for LeaveAction.

These tests verify player leave behavior including removing players
from the game, handling nonexistent players, and edge cases like
the only player leaving.
"""

import pytest

from .connection import LeaveAction
from ..models import GameException, KNIGHT, ARCHER, MAGE
from ..gameplay import (
    GamePlay,
    Player,
    Character,
    CHARACTER_DEFAULT_STATS,
)


def test_leave_action_existing_player():
    """Test a player leaving the game"""
    game = GamePlay()
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = Character(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = LeaveAction("player1", game)
    updated_game = action.run()

    assert "player1" not in updated_game.players
    assert "player2" in updated_game.players  # Other players remain


def test_leave_action_nonexistent_player():
    """Test a player who is not in the game trying to leave"""
    game = GamePlay()
    action = LeaveAction("nonexistent_player", game)

    with pytest.raises(GameException, match="Player not in game"):
        action.run()


def test_leave_action_only_player():
    """Test the only player in the game leaving"""
    game = GamePlay()
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = Character(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)

    action = LeaveAction("player1", game)
    updated_game = action.run()

    assert len(updated_game.players) == 0
