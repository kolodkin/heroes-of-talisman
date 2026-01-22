"""
Tests for DisconnectAction.

These tests verify player disconnection behavior including handling
existing players, nonexistent players, and already disconnected players.
"""

import pytest

from .connection import DisconnectAction
from ..common import (
    GameException,
    CHARACTER_KNIGHT,
    CHARACTER_ARCHER,
    CHARACTER_MAGE,
    STATUS_CONNECTED,
    STATUS_DISCONNECTED,
)
from ..gameplay import (
    GamePlay,
    Player,
    Character,
    CHARACTER_DEFAULT_STATS,
)


def test_disconnect_action_existing_player():
    """Test disconnecting an existing connected player"""
    game = GamePlay()
    characters = {}
    for char_type in [CHARACTER_KNIGHT, CHARACTER_ARCHER, CHARACTER_MAGE]:
        characters[char_type] = Character(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", status=STATUS_CONNECTED, characters=characters)

    action = DisconnectAction("player1", game)
    updated_game = action.run()

    assert updated_game.players["player1"].status == STATUS_DISCONNECTED
    assert updated_game.players["player1"].name == "player1"  # Other data preserved


def test_disconnect_action_nonexistent_player():
    """Test disconnecting a player who is not in the game"""
    game = GamePlay()
    action = DisconnectAction("nonexistent_player", game)

    with pytest.raises(GameException, match="Player not in game"):
        action.run()


def test_disconnect_action_already_disconnected():
    """Test disconnecting a player who is already disconnected"""
    game = GamePlay()
    characters = {}
    for char_type in [CHARACTER_KNIGHT, CHARACTER_ARCHER, CHARACTER_MAGE]:
        characters[char_type] = Character(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", status=STATUS_DISCONNECTED, characters=characters)

    action = DisconnectAction("player1", game)
    updated_game = action.run()

    # Should still work and status remains disconnected
    assert updated_game.players["player1"].status == STATUS_DISCONNECTED
