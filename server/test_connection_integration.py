"""
Integration tests for connection actions.

These tests verify complex scenarios involving multiple actions
and player lifecycle management across connection, disconnection,
and leaving actions.
"""

import pytest

from server.actions.connection import ConnectAction, DisconnectAction, LeaveAction
from server.gameplay.models import (
    GameBoard,
)


def test_connect_then_disconnect_then_reconnect():
    """Test full connection lifecycle: connect -> disconnect -> reconnect"""
    game = GameBoard()

    # Initial connection
    connect_action = ConnectAction("player1", game)
    game = connect_action.run()

    assert game.players_hands["player1"].status == "connected"
    assert game.stage == "start"  # Default stage remains "start"
    assert game.playing == "player1"

    # Disconnect
    disconnect_action = DisconnectAction("player1", game)
    game = disconnect_action.run()

    assert game.players_hands["player1"].status == "disconnected"

    # Reconnect
    reconnect_action = ConnectAction("player1", game)
    game = reconnect_action.run()

    assert game.players_hands["player1"].status == "connected"


def test_multiple_players_connect_disconnect_leave():
    """Test multiple players with various actions"""
    game = GameBoard()

    # Connect multiple players
    for i in range(3):
        player_name = f"player{i+1}"
        connect_action = ConnectAction(player_name, game)
        game = connect_action.run()

    assert len(game.players_hands) == 3
    assert game.playing == "player1"  # First player should be playing

    # Disconnect player2
    disconnect_action = DisconnectAction("player2", game)
    game = disconnect_action.run()

    assert game.players_hands["player2"].status == "disconnected"
    assert len(game.players_hands) == 3  # Still in game

    # Player3 leaves
    leave_action = LeaveAction("player3", game)
    game = leave_action.run()

    assert "player3" not in game.players_hands
    assert len(game.players_hands) == 2

    # Player2 reconnects
    reconnect_action = ConnectAction("player2", game)
    game = reconnect_action.run()

    assert game.players_hands["player2"].status == "connected"
    assert len(game.players_hands) == 2
