"""
Tests for DisconnectAction.

These tests verify player disconnection behavior including handling
existing players, nonexistent players, and already disconnected players.
"""

import pytest

from server.game_engine import GameEngine
from ..models import CONNECT, LEAVE, DISCONNECT
from ..models import (
    GamePlay,
    Player,
    CharacterCard,
    GameException,
    CHARACTER_DEFAULT_STATS,
    KNIGHT,
    ARCHER,
    MAGE,
    CONNECTED,
    DISCONNECTED,
)


def test_disconnect_action_existing_player():
    """Test disconnecting an existing connected player"""
    game = GamePlay()
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", status=CONNECTED, characters=characters)

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(DISCONNECT)

    assert game.players["player1"].status == DISCONNECTED
    assert game.players["player1"].name == "player1"  # Other data preserved


def test_disconnect_action_nonexistent_player():
    """Test disconnecting a player who is not in the game"""
    game = GamePlay()
    engine = GameEngine("test_game", "nonexistent_player", game)

    with pytest.raises(GameException, match="Player not in game"):
        engine.run_action(DISCONNECT)


def test_disconnect_action_already_disconnected():
    """Test disconnecting a player who is already disconnected"""
    game = GamePlay()
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", status=DISCONNECTED, characters=characters)

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(DISCONNECT)

    # Should still work and status remains disconnected
    assert game.players["player1"].status == DISCONNECTED
