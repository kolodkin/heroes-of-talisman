"""
Integration tests for connection actions.

These tests verify complex scenarios involving multiple actions
and player lifecycle management across connection, disconnection,
and leaving actions.
"""

import pytest

from server.game_engine import GameEngine
from ..models import CONNECT, LEAVE, DISCONNECT
from ..models import (
    GamePlay,
    CHARACTER_SELECT,
    CONNECTED,
    DISCONNECTED,
)


def test_connect_then_disconnect_then_reconnect():
    """Test full connection lifecycle: connect -> disconnect -> reconnect"""
    game = GamePlay()

    # Initial connection
    connect_engine = GameEngine("test_game", "player1", game)
    connect_engine.run_action(CONNECT)

    assert game.players["player1"].status == CONNECTED
    assert game.stage == CHARACTER_SELECT
    assert game.active.player == "player1"

    # Disconnect
    disconnect_engine = GameEngine("test_game", "player1", game)
    disconnect_engine.run_action(DISCONNECT)

    assert game.players["player1"].status == DISCONNECTED

    # Reconnect
    reconnect_engine = GameEngine("test_game", "player1", game)
    reconnect_engine.run_action(CONNECT)

    assert game.players["player1"].status == CONNECTED


def test_multiple_players_connect_disconnect_leave():
    """Test multiple players with various actions"""
    game = GamePlay()

    # Connect multiple players
    for i in range(3):
        player_name = f"player{i+1}"
        connect_engine = GameEngine("test_game", player_name, game)
        connect_engine.run_action(CONNECT)

    assert len(game.players) == 3
    assert game.active.player == "player1"  # First player should be active

    # Disconnect player2
    disconnect_engine = GameEngine("test_game", "player2", game)
    disconnect_engine.run_action(DISCONNECT)

    assert game.players["player2"].status == DISCONNECTED
    assert len(game.players) == 3  # Still in game

    # Player3 leaves
    leave_engine = GameEngine("test_game", "player3", game)
    leave_engine.run_action(LEAVE)

    assert "player3" not in game.players
    assert len(game.players) == 2

    # Player2 reconnects
    reconnect_engine = GameEngine("test_game", "player2", game)
    reconnect_engine.run_action(CONNECT)

    assert game.players["player2"].status == CONNECTED
    assert len(game.players) == 2
