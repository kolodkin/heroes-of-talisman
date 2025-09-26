"""
Tests for DisconnectAction.

These tests verify player disconnection behavior including handling
existing players, nonexistent players, and already disconnected players.
"""

import pytest

from server.actions.connection import DisconnectAction
from server.gameplay.models import (
    GameBoard,
    PlayerModel,
    CharacterModel,
    GameException,
    CHARACTER_DEFAULT_STATS,
)


def test_disconnect_action_existing_player():
    """Test disconnecting an existing connected player"""
    game = GameBoard()
    characters = {}
    for char_type in ["knight", "archer", "mage"]:
        characters[char_type] = CharacterModel(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = PlayerModel(name="player1", status="connected", characters=characters)

    action = DisconnectAction("player1", game)
    updated_game = action.run()

    assert updated_game.players["player1"].status == "disconnected"
    assert updated_game.players["player1"].name == "player1"  # Other data preserved


def test_disconnect_action_nonexistent_player():
    """Test disconnecting a player who is not in the game"""
    game = GameBoard()
    action = DisconnectAction("nonexistent_player", game)

    with pytest.raises(GameException, match="Player not in game"):
        action.run()


def test_disconnect_action_already_disconnected():
    """Test disconnecting a player who is already disconnected"""
    game = GameBoard()
    characters = {}
    for char_type in ["knight", "archer", "mage"]:
        characters[char_type] = CharacterModel(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = PlayerModel(name="player1", status="disconnected", characters=characters)

    action = DisconnectAction("player1", game)
    updated_game = action.run()

    # Should still work and status remains disconnected
    assert updated_game.players["player1"].status == "disconnected"
