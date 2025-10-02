"""Test player reordering in GameBoard"""

from server.gameplay.models import GameBoard, Player


def test_reorder_players_single_player():
    """Test reordering with a single player"""
    game = GameBoard(players={"alice": Player(name="alice")})
    game.reorder_players("alice")
    assert list(game.players.keys()) == ["alice"]


def test_reorder_players_two_players():
    """Test reordering with two players"""
    game = GameBoard(
        players={
            "alice": Player(name="alice"),
            "bob": Player(name="bob"),
        }
    )

    # Alice first
    game.reorder_players("alice")
    assert list(game.players.keys()) == ["alice", "bob"]

    # Bob first
    game.reorder_players("bob")
    assert list(game.players.keys()) == ["bob", "alice"]


def test_reorder_players_four_players():
    """Test reordering with four players (circular shift)"""
    game = GameBoard(
        players={
            "alice": Player(name="alice"),
            "bob": Player(name="bob"),
            "charlie": Player(name="charlie"),
            "dave": Player(name="dave"),
        }
    )

    # Alice first
    game.reorder_players("alice")
    assert list(game.players.keys()) == ["alice", "bob", "charlie", "dave"]

    # Bob first
    game.reorder_players("bob")
    assert list(game.players.keys()) == ["bob", "charlie", "dave", "alice"]

    # Charlie first
    game.reorder_players("charlie")
    assert list(game.players.keys()) == ["charlie", "dave", "alice", "bob"]

    # Dave first
    game.reorder_players("dave")
    assert list(game.players.keys()) == ["dave", "alice", "bob", "charlie"]


def test_reorder_players_nonexistent_user():
    """Test reordering with a user that doesn't exist keeps original order"""
    game = GameBoard(
        players={
            "alice": Player(name="alice"),
            "bob": Player(name="bob"),
        }
    )

    game.reorder_players("nonexistent")
    assert list(game.players.keys()) == ["alice", "bob"]
