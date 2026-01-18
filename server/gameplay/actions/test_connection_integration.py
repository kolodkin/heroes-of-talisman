"""
Integration tests for connection actions.

These tests verify complex scenarios involving multiple actions
and player lifecycle management across connection, disconnection,
and leaving actions.
"""

import pytest

from .connection import ConnectAction, DisconnectAction, LeaveAction
from ..models import CHARACTER_SELECT, CONNECTED, DISCONNECTED
from ..gameplay import GamePlay


def test_connect_then_disconnect_then_reconnect():
    """Test full connection lifecycle: connect -> disconnect -> reconnect"""
    game = GamePlay()

    # Initial connection
    connect_action = ConnectAction("player1", game)
    updated_game = connect_action.run()

    assert updated_game.players["player1"].status == CONNECTED
    assert updated_game.stage == CHARACTER_SELECT
    assert updated_game.active.player == "player1"

    # Disconnect
    disconnect_action = DisconnectAction("player1", updated_game)
    updated_game = disconnect_action.run()

    assert updated_game.players["player1"].status == DISCONNECTED

    # Reconnect
    reconnect_action = ConnectAction("player1", updated_game)
    updated_game = reconnect_action.run()

    assert updated_game.players["player1"].status == CONNECTED


def test_multiple_players_connect_disconnect_leave():
    """Test multiple players with various actions"""
    game = GamePlay()

    # Connect multiple players
    for i in range(3):
        player_name = f"player{i+1}"
        connect_action = ConnectAction(player_name, game)
        game = connect_action.run()

    assert len(game.players) == 3
    assert game.active.player == "player1"  # First player should be active

    # Disconnect player2
    disconnect_action = DisconnectAction("player2", game)
    game = disconnect_action.run()

    assert game.players["player2"].status == DISCONNECTED
    assert len(game.players) == 3  # Still in game

    # Player3 leaves
    leave_action = LeaveAction("player3", game)
    game = leave_action.run()

    assert "player3" not in game.players
    assert len(game.players) == 2

    # Player2 reconnects
    reconnect_action = ConnectAction("player2", game)
    game = reconnect_action.run()

    assert game.players["player2"].status == CONNECTED
    assert len(game.players) == 2
