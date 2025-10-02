"""Test player reordering in GameBoard"""

from server.gameplay.models import GameBoard, Player


def test_reorder_players_single_player():
    """Test reordering with a single player"""
    game = GameBoard(players={"alice": Player(name="alice")})
    reordered = game.reorder_players("alice")
    assert list(reordered.keys()) == ["alice"]


def test_reorder_players_two_players():
    """Test reordering with two players"""
    game = GameBoard(
        players={
            "alice": Player(name="alice"),
            "bob": Player(name="bob"),
        }
    )

    # Alice first
    reordered = game.reorder_players("alice")
    assert list(reordered.keys()) == ["alice", "bob"]

    # Bob first
    reordered = game.reorder_players("bob")
    assert list(reordered.keys()) == ["bob", "alice"]


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
    reordered = game.reorder_players("alice")
    assert list(reordered.keys()) == ["alice", "bob", "charlie", "dave"]

    # Bob first
    reordered = game.reorder_players("bob")
    assert list(reordered.keys()) == ["bob", "charlie", "dave", "alice"]

    # Charlie first
    reordered = game.reorder_players("charlie")
    assert list(reordered.keys()) == ["charlie", "dave", "alice", "bob"]

    # Dave first
    reordered = game.reorder_players("dave")
    assert list(reordered.keys()) == ["dave", "alice", "bob", "charlie"]


def test_reorder_players_nonexistent_user():
    """Test reordering with a user that doesn't exist returns original order"""
    game = GameBoard(
        players={
            "alice": Player(name="alice"),
            "bob": Player(name="bob"),
        }
    )

    reordered = game.reorder_players("nonexistent")
    assert list(reordered.keys()) == ["alice", "bob"]
