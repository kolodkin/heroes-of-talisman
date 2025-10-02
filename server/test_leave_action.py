"""
Tests for LeaveAction.

These tests verify player leave behavior including removing players
from the game, handling nonexistent players, and edge cases like
the only player leaving.
"""

import pytest

from server.actions.connection import LeaveAction
from server.gameplay.models import (
    GamePlay,
    Player,
    CharacterCard,
    GameException,
    CHARACTER_DEFAULT_STATS,
)


def test_leave_action_existing_player():
    """Test a player leaving the game"""
    game = GamePlay()
    characters = {}
    for char_type in ["knight", "archer", "mage"]:
        characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])
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
    for char_type in ["knight", "archer", "mage"]:
        characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)

    action = LeaveAction("player1", game)
    updated_game = action.run()

    assert len(updated_game.players) == 0
